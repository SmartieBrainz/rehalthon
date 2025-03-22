# SETUP VENV (OPTIONAL - RECOMMENDED)
#python -m venv eduthon
#eduthon\Scripts\activate

# INSTALL REQUIREMENTS
#pip install flask flask_mail flask_wtf mysql.connector

# RUN THE APP IN LOCAL NETWORK
#flask run --host=0.0.0.0 --port=5000

from os import path

from flask import Flask, request, render_template, redirect, url_for, session , flash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from mysql.connector import Error as MySQLError

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import db_joinrequests
from db_users import DB_Users
from db_teams import DB_Teams
from db_teammembers import DB_TeamMembers
from db_joinrequests import DB_JoinRequests
from functools import wraps

# TODOs:
# [ ] Check email sending time out issue (email doesnt reach client)
# [ ] Add Logger and save logs into info,errors

app = Flask(__name__)
app.secret_key = r"eGL8)B*[Ipq%R4^c~9cw~tX%M"

# Configuration for Flask-Mail
#app.config['MAIL_USERNAME'] = 'web@eduthon.sa'  # Enter your email
#app.config['MAIL_PASSWORD'] = '0eBMYmzZmzyo1fCV'  # Enter your email password
#app.config['MAIL_SERVER'] = 'email.t2.sa'
#app.config['MAIL_PORT'] = 587
#app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USE_SSL'] = False

# Configuration for Flask-Mail gmail

app.config['MAIL_SERVER'] = "live.smtp.mailtrap.io"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = "rehalhackathon@gmail.com"
app.config['MAIL_PASSWORD'] = r"q^N':aFG<(=hSh\JF&mS%-:i>"

mail = Mail(app)

# TODO: add env file and access values from there
app.config['SECRET_KEY'] = r"!u/ZsV-)j%m><Ytqa7CHW&ZlC"  # Make sure to set a secret key
app.config['SECURITY_PASSWORD_SALT'] = r"/H19CKdG=.)Nmf~Vb.aa2cPAP"  # Set a security salt

app.config['UPLOAD_FOLDER'] = "/path/to/upload" # CHANGE
app.config['MAX_CONTENT_LENGTH'] = 32 * 1000 * 1000 # 32MB


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )

    except Exception as e:
        return False

    return email


def send_email(to, subject, template):
    try:
        msg = Message(
            subject,
            sender=app.config['MAIL_USERNAME'],
            recipients=[to],
            html=template
        )
        mail.send(msg)

    except Exception as e:
        print("Couldn't send email: %s" % e)
        return None


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id is None:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))

        # Assuming DB_Users.get_user_by_id(user_id) returns a dictionary of user information
        user = DB_Users.get_user_by_id(user_id)
        if user and user['is_admin']=='1':
            return f(*args, **kwargs)
        else:
            flash('You do not have permission to view this page.', 'danger')
            return redirect(url_for('home'))

    return decorated_function


def confirmed_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id is None:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))

        user_confirmed = DB_Users.get_user_confirmation_status(user_id)
        if not user_confirmed:
            flash('Please confirm your email address first.', 'warning')
            return redirect(url_for('dashboard'))

        return f(*args, **kwargs)

    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))

        return f(*args, **kwargs)

    return decorated_function


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )

    except Exception as e:
        return None

    return email


def check_mimetype(mime_type: str) -> bool:
    mime_type_whitelist = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    ]

    if mime_type in mime_type_whitelist:
        return True

    return False


def check_extension(filename: str) -> bool:
    extensions_whitelist = ["pdf", "pptx", "docx"]
    extension = filename.split(".")[-1]

    if extension in extensions_whitelist:
        return True

    return False

# TODO: change for FileStorage object in `request.files.get()`
def check_magic_bytes(fd: int) -> bool:
    magic_bytes_whitelist = {
            b"\x25\x50\x44\x46\x2D": 5,     # pdf files
            b"\x50\x4B\x03\x04": 4,         # (docx, pptx) files
            b"\x50\x4B\x05\x06": 4,         # (docx, pptx) empty archive
            b"\x50\x4B\x07\x08": 4          # (docx, pptx) spanned archive
        }

    for magic_bytes in magic_bytes_whitelist:
        fd.seek(0)
        magic_size = magic_bytes_whitelist[magic_bytes]
        head_bytes = fd.read(magic_size)
        if head_bytes == magic_bytes:
            return True

    return False


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/admin_dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')


@app.route('/admin/teams')
@login_required
@admin_required
def admin_teams():
    teams = DB_Teams.get_all_teams_dict()
    return render_template('admin_teams.html', teams=teams)


@app.route('/admin/teams/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_team():
    if request.method == 'POST':
        team_name = request.form['team_name']
        created_by = session['user_id']  # Assuming the admin is creating the team
        team_data = {
            'team_name': team_name,
            'created_by': created_by
        }
        DB_Teams.create_team(team_data)
        return redirect(url_for('admin_teams'))
    return render_template('admin_add_team.html')


@app.route('/admin/teams/delete/<int:team_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_team(team_id):
    DB_Teams.delete_team(team_id)
    return redirect(url_for('admin_teams'))


@app.route('/admin/teams/members/<int:team_id>')
@login_required
@admin_required
def admin_team_members(team_id):
    members = DB_TeamMembers.get_team_members(team_id)
    return render_template('admin_team_members.html', members=members, team_id=team_id)


@app.route('/admin/teams/members/add/<int:team_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_team_member(team_id):
    if request.method == 'POST':
        user_id = request.form['user_id']
        DB_TeamMembers.add_team_member(team_id, user_id)
        return redirect(url_for('admin_team_members', team_id=team_id))

    # Retrieve users not in the team to display in the form
    return render_template('admin_add_team_member.html', team_id=team_id)


@app.route('/admin/teams/members/remove/<int:team_id>/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_remove_team_member(team_id, user_id):
    DB_TeamMembers.remove_team_member(team_id, user_id)
    return redirect(url_for('admin_team_members', team_id=team_id))



# @app.route('/send_test_email')
# def send_test_email():
#     msg = Message('Test Email', sender='eduthon.ftc@gmail.com', recipients=['misharialbuhari@gmail.com'], body='This is a test email.')
#     try:
#         mail.send(msg)
#         return 'Email sent successfully!'
#     except Exception as e:
#         print(e)
#         return f'Failed to send email. Error: {str(e)}'


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        msg = Message(f'Contact Us Submission from {name}',
                      sender=email,
                      recipients=['web@eduthon.sa'], #CHANGE
                      body=f"Name: {name}\nEmail: {email}\nMessage: {message}")
        
        try:
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
            
        except Exception as e:
            flash('Your message could not be sent. Please try again later.', 'danger')

        return redirect(url_for('contact'))
    return render_template('contact.html')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    user_data = {
        'full_name': '',
        'username': '',
        'email': '',
        'password_hash': '',
        'phone_number': '',
        'dob': '',
        'gender': '',
        'role': '',
        'city': '',
        'educational_level': '',
        'university': '',
        'major': '',
        'job_title': '',
        'industry': '',
        'bio': '',
        'linkedin_url': '',
        'twitter_handle': '',
        'github_username': ''
    }

    if request.method == 'POST':
        educational_level = request.form['educational_level']
        if educational_level == 'other':
            educational_level = request.form.get('otherEducationalLevel', '')

        university = request.form['university']
        if university == 'other':
            university = request.form.get('otherUniversity', '')

        # Safely access 'major' using .get() to avoid KeyError
        major = request.form.get('major', '')  # Default to an empty string if 'major' does not exist
        if major == 'other':
            major = request.form.get('otherMajor', '')

        job_title = request.form['job_title']
        if job_title == 'other':
            job_title = request.form.get('industryCompany', '')

        role = request.form.get('role')
        if role == 'أخرى':
            role = request.form.get('otherRole', '')

        user_data = {
            'full_name': request.form['full_name'],
            'username': request.form['username'],
            'email': request.form['email'],
            'password_hash': generate_password_hash(request.form['password']),
            'phone_number': request.form['phone_number'],
            'dob': request.form['dob'],
            'gender': request.form.get('gender', ''),
            'role': role,
            'city': request.form.get('city', ''),
            'educational_level': educational_level,
            'university': university,
            'major': major,
            'job_title': job_title,
            'industry' : request.form.get('industry', ''),
            'bio': request.form['bio'],
            'linkedin_url': request.form['linkedin_url'],
            'twitter_handle': request.form['twitter_handle'],
            'github_username': request.form['github_username']
        }

        try:
            if DB_Users.email_exists(user_data['email']):
                flash('Email already exists. Please choose a different email.', 'warning')
                return render_template('register.html', user_data=user_data)
            
            if DB_Users.username_exists(user_data['username']):
                flash('Username already exists. Please choose a different username.', 'warning')
                return render_template('register.html', user_data=user_data)
            
            if len(user_data['password_hash']) < 6:
                flash('password must contain at least 6 characters', 'warning')
                return render_template('register.html', user_data=user_data)

            user_id = DB_Users.add_user(user_data)

            if user_id:
                token = generate_confirmation_token(user_data['email'])
                confirm_url = url_for('confirm_email', token=token, _external=True)
                html = render_template('activate_account.html', confirm_url=confirm_url)
                subject = "Please confirm your email"

                try:
                    send_email(user_data['email'], subject, html)
                    flash('A confirmation email has been sent. Please check your email to complete registration.', 'warning')

                except Exception as e:
                    flash('Failed to send confirmation email. Please try again later.', 'danger')

                return redirect(url_for('home'))
            
            else:
                flash('Failed to register. Please try again.', 'danger')

        except Exception as e:
            flash(f'An error occurred: {e}', 'danger')

    # when register closes, render regClosed.html instead, and comment all previous code
    return render_template('register.html', user_data=user_data)


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)

        if email:
            user = DB_Users.get_user_by_email(email)

            if user and not user['confirmed']==0:
                DB_Users.confirm_user(user['email'])
                flash('Your email address has been confirmed.', 'success')
                return redirect(url_for('dashboard'))

            else:
                flash('Account already confirmed or user does not exist.', 'info')

        else:
            flash('The confirmation link is invalid or has expired.', 'danger')

    except Exception as e:
        flash(str(e), 'danger')

    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    username, password = None, None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            user_id = DB_Users.authenticate(username, password)

            if user_id:
                session['user_id'] = user_id
                session['username'] = username
                DB_Users.update_last_login(user_id) # Update last login date
                return redirect(url_for('show_teams'))

            else:
                flash('Login failed. Please check your username and password.', 'warning')

        except Exception as e:
            flash(f"something went wrong: {e}",'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    try:
        user_id = session.get('user_id')
        user = DB_Users.get_user_by_id(user_id)
        is_email_confirmed = user['confirmed'] == 1

        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('home'))

        if request.method == 'POST':
            role = request.form.get('role')
            if role == 'أخرى':
                role = request.form.get('otherRole')

            user_data = {
                'full_name': request.form.get('full_name'),
                'phone_number': request.form.get('phone_number'),
                'role': role,
                'bio': request.form.get('bio'),
                'linkedin_url': request.form.get('linkedin_url'),
                'twitter_handle': request.form.get('twitter_handle'),
                'github_username': request.form.get('github_username'),
            }

            DB_Users.update_user_info(user_id, user_data)
            return redirect(url_for('show_teams'))

        return render_template('dashboard.html', user=user, is_email_confirmed=is_email_confirmed)

    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('show_teams'))

"""
TODO:
[ ] Add deadline timer for submitting the project
"""
@app.route("/upload_final_project", methods=["GET", "POST"])
@login_required
@confirmed_required
def upload_final_project():
    user_id = session.get("user_id")

    if DB_Teams.is_user_member_of_team(user_id):
        team_id, team_name = DB_Teams.get_user_team(user_id)
        is_leader = DB_Teams.is_leader(team_id, user_id)
        members = DB_Teams.get_team_members(team_id)
        team_pending_requests = DB_JoinRequests.get_join_requests_for_team(team_id) if is_leader else None
        leader_id = DB_Teams.get_team_leader_by_team_id(team_id)[0]
        is_project_uploaded = DB_Teams.is_project_uploaded(team_id)

    if request.method == "POST":
        try:
            project_file = request.files.get("project_file")
            project_name = secure_filename(project_file.filename)
            if project_name == '':
                flash("No file submitted.", "danger")
            
            if not check_mimetype(project_file.mimetype):
                flash("File could not be uploaded.\nReason: Please check file name and extension. (only pdf, pptx, and docx are allowed)", "danger")
            
            if not check_extension(project_file.filename):
                flash("File could not be uploaded.\nReason: Please check file name and extension. (only pdf, pptx, and docx are allowed)", "danger")
            
            if not check_magic_bytes():
                flash("File could not be uploaded.\nReason: Please check file for corruptions.", "danger")

            return redirect(url_for("my_team"))

        except Exception as e:
            flash(f"File could not be uploaded.\nReason: {e}", "danger")
            return redirect(url_for("my_team"))

    if is_leader and not is_project_uploaded:
        name, ext, *_ = project_name.split('.') #Assuming file name would be two or more values
        filename = name+'_'+team_name+'.'+ext
        project_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        DB_Teams.update_project_upload_status(team_id, True)

    else:
        flash("Could not upload file\nReason: project already submitted.", "danger")
        return redirect(url_for("my_team"))


    return render_template("my_team.html", team_name=team_name, user_id=user_id, team_id=team_id, is_leader=is_leader, members=members, team_pending_requests=team_pending_requests, leader_id=leader_id, is_project_uploaded=is_project_uploaded)


# PREVIOUSLY USED DASHBOARD ROUTE

# @app.route('/dashboard', methods=['GET', 'POST'])
# @login_required
# def dashboard():
#     user_id = session.get('user_id')
#     user = DB_Users.get_user_by_id(user_id)  # Retrieve user data from the database

#     # if request.method == 'POST':
#     #     # Extract form data
#     #     user_data = {
#     #         'full_name': request.form.get('full_name'),
#     #         'phone_number': request.form.get('phone_number'),
#     #         'gender': request.form.get('gender'),
#     #         'role': request.form.get('role'),
#     #         'bio': request.form.get('bio'),
#     #         'linkedin_url': request.form.get('linkedin_url'),
#     #         'twitter_handle': request.form.get('twitter_handle'),
#     #         'github_username': request.form.get('github_username'),
#     #         # Add other fields as necessary
#     #     }

#     #     # Update user information in the database
#     #     DB_Users.update_user_info(user_id, user_data)
#     #     flash('Your information has been updated successfully.', 'success')
#     #     return redirect(url_for('dashboard'))

#     # For a GET request, display the current user information
#     if not user:
#         flash("User not found.", "danger")
#         return redirect(url_for('home'))
#     is_email_confirmed = user['confirmed'] == 1
#     # print(user['confirmed'])
#     return render_template('dashboard.html', user=user, is_email_confirmed=is_email_confirmed)


# @app.route('/dashboard', methods=['GET', 'POST'])
# @login_required
# def dashboard():
#     user_id = session.get('user_id')
#     # Fetch user data from the database
#     user_data = DB_Users.get_user_by_id(user_id)
#     if not user_data:
#         flash("User not found.", "danger")
#         return redirect(url_for('home'))
    
#     if request.method == 'POST':
#         # Extract data from form submission
#         full_name = request.form.get('full_name')
#         phone_number = request.form.get('phone_number')
#         gender = request.form.get('gender')
#         role = request.form.get('role')
#         bio = request.form.get('bio')
#         linkedin_url = request.form.get('linkedin_url')
#         twitter_handle = request.form.get('twitter_handle')
#         github_username = request.form.get('github_username')
        
#         # Prepare the user_data dictionary with updated values
#         updated_user_data = {
#             'full_name': full_name,
#             'phone_number': phone_number,
#             'gender': gender,
#             'role': role,
#             'bio': bio,
#             'linkedin_url': linkedin_url,
#             'twitter_handle': twitter_handle,
#             'github_username': github_username,
#         }

#         # Update user data in the database
#         try:
#             DB_Users.update_user_info(user_id, updated_user_data)
#             flash('Profile updated successfully.', 'success')
#         except Exception as e:
#             flash('An error occurred while updating the profile.', 'danger')
#             print(e)
        
#         # Fetch updated user data to reflect changes in the form
#         user_data = DB_Users.get_user_by_id(user_id)

#     return render_template('dashboard.html', user_data=user_data)


@app.route('/teams')
@login_required
def show_teams():
    try:
        user_id = session.get('user_id')
        teams = DB_Teams.get_all_teams()

        # This dictionary will hold team_id as the key and a list of member details as the value
        teams_members = {}
        for team in teams:
            team_id = team[0]
            teams_members[team_id] = DB_TeamMembers.get_team_members(team_id)

        is_leader = DB_Teams.user_is_leader(user_id)
        is_member = DB_Teams.is_user_member_of_team(user_id)
        boolean_pending_request = DB_JoinRequests.has_pending_request(user_id)
        user_pending_requests = DB_JoinRequests.get_user_pending_requests(user_id)

    except Exception as e:
        flash(f"An error occurred: {e}", 'danger')
        return redirect(url_for('home'))

    return render_template('teams.html', teams=teams, teams_members=teams_members, is_leader=is_leader, is_member=is_member, boolean_pending_request=boolean_pending_request, user_pending_requests=user_pending_requests)


@app.route('/resend_confirmation' , methods=['GET', 'POST'])
@login_required
def resend_confirmation():
    try:
        user_id = session.get('user_id')
        user_data = DB_Users.get_user_by_id(user_id)

        if user_data and user_data['confirmed'] == 0:
            token = generate_confirmation_token(user_data['email'])
            confirm_url = url_for('confirm_email', token=token, _external=True)
            html = render_template('activate_account.html', confirm_url=confirm_url)  # Ensure you have this template
            subject = "Please confirm your email"
            send_email(user_data['email'], subject, html)
            flash('A new confirmation email has been sent. Please check your email.', 'info')

        else:
            flash('Your email is already confirmed', 'warning')

    except Exception as e:  
        flash(f"An error occurred: {e}", 'danger')

    return redirect(url_for('dashboard'))


@app.route('/create_team', methods=['GET', 'POST'])
@login_required
@confirmed_required
def create_team():
    user_id = session['user_id']

    if DB_Teams.is_user_member_of_team(user_id) or DB_JoinRequests.has_pending_request(user_id):
        flash("You cannot create a team while being part of a team or having a pending join request.", "warning")
        return redirect(url_for('show_teams') )

    if DB_Teams.is_user_member_of_team(user_id):
        flash("You are already in a team.", "warning")
        return redirect(url_for('show_teams'))

    if request.method == 'POST':
        team_name = request.form['team_name']
        try:
            team_id = DB_Teams.create_team({'team_name': team_name, 'created_by': user_id})

        except MySQLError as e:
            if e.errno == 1062:
                flash('This team name is already taken. Please choose another.', 'warning')
            else:
                flash('An error occurred while adding the team. Please try again.', 'danger')
            return redirect(url_for('create_team'))

        if team_id:
            flash("Team created successfully.", "success")
            return redirect(url_for('show_teams'))
        else:
            flash("An error occurred while creating the team.", "danger")

    return render_template('create_team.html')


@app.route('/request_to_join/<int:team_id>', methods=['POST'])
@login_required
@confirmed_required
def request_to_join(team_id):
    user_id = session.get('user_id')
    user_full_name = DB_Users.get_user_full_name(user_id)

    try:
        if DB_JoinRequests.has_pending_request(user_id):
            flash('You already have a pending join request to a team.', 'danger')
            return redirect(request.referrer)

        if DB_Teams.is_user_member_of_team(user_id):
            flash('You are already a member of this team.', 'danger')
            return redirect(request.referrer)

        if DB_JoinRequests.has_pending_request(user_id):
            flash('You already have a pending join request to a team.', 'danger')
            return redirect(request.referrer)

        success = DB_JoinRequests.create_join_request({'team_id': team_id, 'user_id': user_id})
        if not success:
            flash('Unable to create a join request at this time.', 'danger')
            return redirect(request.referrer)

        team_leader_id = DB_Teams.get_leader(team_id)
        team_leader_email = DB_Users.get_user_email_by_id(team_leader_id)

        if team_leader_email:
            subject = "New Join Request"
            template = f" {user_full_name} has requested to join your team. \n you can accept or reject the request from ""فريقي"" page at eduthon.sa" #CHANGE
            send_email(team_leader_email, subject, template)

        flash('Your request to join the team has been sent.', 'success')
        return redirect(request.referrer)

    except ValueError as e:
        flash(str(e), 'error')
        return redirect(request.referrer)

    except Exception as e:
        flash('An unexpected error occurred: {}'.format(str(e)), 'danger')
        raise e
        return redirect(request.referrer)


#   GOOD BUT DOESNT SEND EMAIL
#
# @app.route('/request_to_join/<int:team_id>', methods=['POST'])
# @login_required
# @confirmed_required
# def request_to_join(team_id):
#     user_id = session.get('user_id')

#     try:
#         if DB_JoinRequests.has_pending_request(user_id):
#             flash('You already have a pending join request to a team.', 'danger')
#             return redirect(request.referrer)
#         # Check if the user is the team leader
#         if DB_Teams.user_is_leader(user_id):
#             flash('Team leaders cannot join their own team.', 'danger')
#             return redirect(request.referrer)

#         # Check if the user is already a member of the team
#         if DB_Teams.is_user_member_of_team(user_id):
#             flash('You are already a member of this team.', 'danger')
#             return redirect(request.referrer)

#         # Check if the user has any existing pending requests to join any team
#         if DB_JoinRequests.has_pending_request(user_id):
#             flash('You already have a pending join request to a team.', 'danger')
#             return redirect(request.referrer)

#         # Proceed with creating a new join request
#         success = DB_JoinRequests.create_join_request({'team_id': team_id, 'user_id': user_id})
#         if not success:
#             print("not success")
#             flash('Unable to create a join request at this time.', 'danger')
#             return redirect(request.referrer)

#         flash('Your request to join the team has been sent.', 'success')
#         return redirect(request.referrer)

#     except ValueError as e:
#         # Handle known errors
#         flash(str(e), 'error')
#         return redirect(request.referrer)
#     except Exception as e:
#         # Handle unexpected errors
#         flash('An unexpected error occurred: {}'.format(str(e)), 'danger')
#         raise e

#         return redirect(request.referrer)


@app.route('/teamRequests/<int:team_id>')
@login_required
@confirmed_required
def team_requests(team_id):
    if not DB_Teams.is_leader(team_id, session['user_id']):
        return "Unauthorized", 403

    join_requests = DB_JoinRequests.get_join_requests_for_team(team_id)
    team_name = DB_Teams.get_user_team(session['user_id'])[1]
    return redirect(url_for('my_team'))


# @app.route('/accept_request/<int:request_id>/<int:team_id>', methods=['POST'])
# @login_required
# @confirmed_required
# def accept_request(request_id, team_id):
#     if DB_Teams.get_team_member_count(team_id) >= 5:
#         flash('The team already has the maximum number of members (5).', 'warning')
#         return redirect(url_for('my_team'))
#     user_id = session['user_id']
#     if DB_JoinRequests.accept_join_request(request_id, team_id, user_id):
#         return redirect(url_for('team_requests', team_id=team_id))
#     return "Unauthorized", 403 #@app.route('/reject_request/<int:request_id>/<int:team_id>', methods=['POST']))


@app.route('/accept_request/<int:request_id>/<int:team_id>', methods=['POST'])
@login_required
@confirmed_required
def accept_request(request_id, team_id):
    requester_id = DB_JoinRequests.get_requester_id(request_id)
    if not requester_id:
        flash("Requester not found.", "danger")
        return redirect(url_for('team_requests', team_id=team_id))

    if DB_Teams.get_team_member_count(team_id) >= 5:
        flash('The team already has the maximum number of members (5).', 'warning')
        return redirect(url_for('my_team'))
    
    user_id = session['user_id']
    if DB_JoinRequests.accept_join_request(request_id, team_id, user_id):
        requester_email = DB_Users.get_user_email_by_id(requester_id)
        team_name = DB_Teams.get_team_name(team_id)
        
        if requester_email:
            send_email(requester_email, "Join Request Accepted", f"Your request to join the team {team_name} has been accepted.")
            
        flash('Join request accepted.', 'success')
        return redirect(url_for('team_requests', team_id=team_id))
    
    else:
        flash('Unable to process the request.', 'danger')
        return redirect(url_for('team_requests', team_id=team_id))


# @app.route('/reject_request/<int:request_id>/<int:team_id>', methods=['POST'])
# @login_required
# def reject_request(request_id, team_id):
#     user_id = session['user_id']
#     if DB_JoinRequests.reject_join_request(request_id, team_id, user_id):
#         return redirect(url_for('team_requests', team_id=team_id))
#     return "Unauthorized", 403
    

@app.route('/reject_request/<int:request_id>/<int:team_id>', methods=['POST'])
@login_required
def reject_request(request_id, team_id):
    requester_id = DB_JoinRequests.get_requester_id(request_id)
    if not requester_id:
        flash("Requester not found.", "danger")
        return redirect(url_for('team_requests', team_id=team_id))

    user_id = session['user_id']
    if DB_JoinRequests.reject_join_request(request_id, team_id, user_id):
        requester_email = DB_Users.get_user_email_by_id(requester_id)
        team_name = DB_Teams.get_team_name(team_id)
        
        if requester_email:
            send_email(requester_email, "Join Request Rejected", f"Your request to join the team {team_name} has been rejected.")
            
        flash('Join request rejected.', 'success')
        return redirect(url_for('team_requests', team_id=team_id))
    
    else:
        flash('Unable to process the request.', 'danger')
        return redirect(url_for('team_requests', team_id=team_id))


# @app.route('/team_members/<int:team_id>')
# @login_required
# def team_members(team_id):
#     user_id = session['user_id']
#     is_leader = DB_Teams.is_leader(team_id, user_id)
#     members = DB_Teams.get_team_members(team_id)
#     return render_template('team_members.html', members=members, team_id=team_id, is_leader=is_leader)
#
#     members = DB_Teams.get_team_members(team_id)
#     return render_template('team_members.html', members=members, team_id=team_id)

@app.route('/remove_member/<int:team_id>/<int:user_id>', methods=['POST'])
@login_required
@confirmed_required
def remove_member(team_id, user_id):
    leader_id = session['user_id']
    if DB_Teams.remove_member(team_id, user_id, leader_id):
        return redirect(url_for('my_team', team_id=team_id))
    else:
        return "Unauthorized or Error", 403  # If the user is not the team leader or an error occurred


# @app.route('/delete_team/<int:team_id>', methods=['POST'])
# @login_required
# @confirmed_required
# def delete_team(team_id):
#     user_id = session['user_id']
#     if DB_Teams.is_leader(team_id, user_id):
#         DB_Teams.delete_team(team_id)
#         return redirect(url_for('show_teams'))
#     return "Unauthorized", 403



# WORKING PERFECTLY
# @app.route('/delete_team/<int:team_id>', methods=['POST'])
# @login_required
# @confirmed_required
# def delete_team_route(team_id):
#     user_id = session['user_id']
#     if DB_Teams.is_leader(team_id, user_id):
#         DB_Teams.delete_team(team_id)
#         return redirect(url_for('show_teams'))
#     else:
#         flash("Unauthorized action.", "danger")
#         return redirect(url_for('show_teams'))
    


@app.route('/delete_team/<int:team_id>', methods=['POST'])
@login_required
@confirmed_required
def delete_team(team_id):
    user_id = session.get('user_id')
    if DB_Teams.is_leader(team_id, user_id):
        member_emails = DB_TeamMembers.get_team_member_emails(team_id)
        team_name = DB_Teams.get_team_name(team_id)

        if DB_Teams.delete_team(team_id):
            subject = "Team Deletion Notification"
            template = f"<html><body><p>We're sorry to inform you that your team, '{team_name}', has been deleted.</p></body></html>"
            for email in member_emails:
                send_email(to=email, subject=subject, template=template)
            
            flash(f"Team '{team_name}' deleted successfully. All members have been notified.", "success")
        else:
            flash("An error occurred while deleting the team. Please try again.", "danger")

    else:
        flash("Unauthorized action. You are not allowed to delete this team.", "danger")

    return redirect(url_for('show_teams'))


# @app.route('/leave_team/<int:team_id>', methods=['POST'])
# @login_required
# @confirmed_required
# def leave_team(team_id):
#     user_id = session.get('user_id')
#     result = DB_Teams.remove_member(team_id, user_id, user_id)

#     if result == "Success":
#         flash("You have successfully left the team.", "success")
#     elif result == "Member not found.":
#         flash("You are not a member of this team.", "danger")
#     else:
#         flash("An error occurred while trying to leave the team.", "danger")

#     return redirect(url_for('show_teams'))
    

@app.route('/leave_team/<int:team_id>', methods=['POST'])
@login_required
@confirmed_required
def leave_team(team_id):
    user_id = session.get('user_id')
    team_leader = DB_Teams.get_leader(team_id)
    if not team_leader:
        flash("Team leader not found.", "danger")
        return redirect(url_for('show_teams'))

    team_name = DB_Teams.get_team_name(team_id)
    if not team_name:
        flash("Team not found.", "danger")
        return redirect(url_for('show_teams'))

    leader_email = DB_Users.get_user_email_by_id(team_leader)
    user_full_name = DB_Users.get_user_full_name(user_id)
    result = DB_Teams.remove_member(team_id, user_id, user_id)

    if result == "Success":
        flash("You have successfully left the team.", "success")
        if leader_email:
            subject = f"{user_full_name} has left the team {team_name}"
            message = f"Dear Team Leader,\n\nThis is to inform you that {user_full_name} has left the team '{team_name}'.\n\nBest Regards,\nEduthon Team" #CHANGE
            send_email(to=leader_email, subject=subject, template=message)

    elif result == "Member not found.":
        flash("You are not a member of this team.", "danger")
    else:
        flash("An error occurred while trying to leave the team.", "danger")

    return redirect(url_for('show_teams'))


@app.route('/my_pending_requests')
@login_required
@confirmed_required
def my_pending_requests():
    user_id = session.get('user_id')
    pending_requests = DB_JoinRequests.get_user_pending_requests(user_id)

    # Fetch additional details about the teams if necessary
    teams_info = []
    for team_id in pending_requests:
        team_info = DB_Teams.get_team_info(team_id)
        teams_info.append(team_info)

    return render_template('pending_requests.html', teams_info=teams_info)


@app.route('/my_team')
@login_required
@confirmed_required
def my_team():
    user_id = session.get('user_id')

    if DB_Teams.is_user_member_of_team(user_id):
        team_id,team_name = DB_Teams.get_user_team(user_id)
        is_leader = DB_Teams.is_leader(team_id, user_id)
        members = DB_Teams.get_team_members(team_id)
        team_pending_requests = DB_JoinRequests.get_join_requests_for_team(team_id) if is_leader else None
        leader_id = DB_Teams.get_team_leader_by_team_id(team_id)[0]
        is_project_uploaded = DB_Teams.is_project_uploaded(team_id)

        return render_template('my_team.html',team_name=team_name, user_id=user_id, team_id=team_id, is_leader=is_leader, members=members, team_pending_requests=team_pending_requests, leader_id=leader_id, is_project_uploaded=is_project_uploaded)

    hasPending = DB_JoinRequests.has_pending_request(user_id)
    if hasPending:
        team_id = DB_Teams.get_team_id_by_requester_id(user_id)
        team_name = DB_Teams.get_team_name_by_requester_id(user_id)
        return render_template('my_team.html',team_id=team_id, user_id=user_id, team_name=team_name,hasPending=hasPending)
    else:
        if not hasPending and not DB_Teams.is_user_member_of_team(user_id):
            flash('You are not a part of any team.', 'warning')

    return redirect(url_for('show_teams'))


@app.route('/cancel_join_request/<int:team_id>', methods=['POST'])
@login_required
@confirmed_required
def cancel_join_request(team_id):
    user_id = session.get('user_id')
    if DB_JoinRequests.cancel_join_request(user_id, team_id):
        flash('Join request canceled successfully.', 'success')
    else:
        flash('Failed to cancel join request.', 'danger')
    return redirect(url_for('my_team'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# @app.route('/password_reset/<token>', methods=['GET', 'POST'])
# def password_reset(token):
#     try:
#         email = confirm_token(token)
#     except:
#         flash('The password reset link is invalid or has expired.', 'danger')
#         return redirect(url_for('login'))

#     if request.method == 'POST' :
#         new_password = request.form.get('new_password')
#         if len(new_password) < 6:
#             flash('password must contain at least 6 characters', 'warning')
#             return render_template('password_reset.html', token=token)

#         # Update the user's password
#         DB_Users.update_password(email, new_password)
#         flash('Your password has been updated.', 'success')
#         return redirect(url_for('login'))
#     return render_template('password_reset.html', token=token)@app.route('/password_reset/<token>', methods=['GET', 'POST'])


@app.route('/password_reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    try:
        email = confirm_token(token)
    except:
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not new_password or not confirm_password:
            flash('Please fill out both password fields.', 'warning')
            return render_template('password_reset.html', token=token)

        if new_password != confirm_password:
            flash('Passwords do not match.', 'warning')
            return render_template('password_reset.html', token=token)

        if len(new_password) < 6:
            flash('Password must contain at least 6 characters.', 'warning')
            return render_template('password_reset.html', token=token)

        hashed_password = generate_password_hash(new_password)
        DB_Users.update_password(email, hashed_password)
        flash('Your password has been updated.', 'success')
        return redirect(url_for('login'))

    return render_template('password_reset.html', token=token)


@app.route('/send_password_reset', methods=['GET', 'POST'])
def send_password_reset():
    if request.method == 'POST':
        email = request.form.get('email')
        user = DB_Users.get_user_by_email(email)
        if user:
            attempts = DB_Users.check_reset_attempts(user['id'])
            if attempts < 10:
                DB_Users.record_password_reset_attempt(user['id'])
                send_password_reset_email(email)
                flash('If an account with this email exists, a password reset email has been sent.', 'info')
            else:
                flash('You have exceeded the maximum number of password reset attempts. Please try again later.', 'danger')
        else:
            flash('If an account with this email exists, a password reset email has been sent.', 'info')
        return redirect(url_for('login'))
    return render_template('password_reset_request.html')


def send_password_reset_email(user_email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = serializer.dumps(user_email, salt='password-reset-salt')
    reset_url = url_for('password_reset', token=token, _external=True)
    
    msg = Message('Password Reset Request', recipients=[user_email], sender='eduthon.ftc@gmail.com') #CHANGE
    msg.body = f'Please click on the link to reset your password: {reset_url}'
    
    mail.send(msg)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
