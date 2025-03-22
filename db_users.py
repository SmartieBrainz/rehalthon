from flask import flash
from database import Database
from werkzeug.security import generate_password_hash, check_password_hash
class DB_Users:



                            # THIS IS FOR ONLY USERNAME,EMAIL,PASSWORD
    # @staticmethod
    # def add_user(user_data):
    #     connection = None
    #     try:
    #         connection = Database.connect_mysql()
    #         cursor = connection.cursor()
    #         cursor.execute(
    #             "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
    #             (user_data['username'], user_data['email'], user_data['password_hash']))
    #         connection.commit()
    #         return cursor.lastrowid
    #     except Exception as e:
    #         print(f"An error occurred: {e}")
    #         raise e
    #     finally:
    #         if connection:
    #             connection.close()

    @staticmethod
    def add_user(user_data):
        connection = None
        try:
            connection = Database.connect_mysql()
            cursor = connection.cursor()
            sql = """INSERT INTO users (full_name, username, email, password_hash, phone_number,gender,role, dob, city, 
                     educational_level, university, major, job_title, industry, bio, linkedin_url, twitter_handle, github_username) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s)"""
            values = (user_data['full_name'], user_data['username'], user_data['email'],
                      user_data['password_hash'],
                      user_data['phone_number'],
                      user_data['gender'], user_data['role'],
                      user_data['dob'], user_data['city'],
                      user_data['educational_level'],
                      user_data['university'], user_data['major'], user_data['job_title'], user_data['industry'],
                      user_data['bio'],
                      user_data['linkedin_url'], user_data['twitter_handle'],
                      user_data['github_username'])
            cursor.execute(sql, values)
            connection.commit()
            return cursor.lastrowid
        except Exception as e:
            raise e
        finally:
            if connection:
                connection.close()

    # def authenticate(username, password):
    #     connection = Database.connect_mysql()
    #     try:
    #         cursor = connection.cursor()
    #         cursor.execute("SELECT id , password_hash FROM users WHERE username = %s ", (username)
    #         user_id = cursor.fetchone()
    #         return user_id[0] if user_id else None
    #     except Exception as e:
    #         print(f"An error occurred: {e}")
    #     finally:
    #         if connection:
    #             connection.close()
    def authenticate(username, password):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            # Retrieve the user's hashed password from the database
            cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            
            if result:
                user_id, stored_password_hash = result
                # Verify the provided password against the stored hash
                if check_password_hash(stored_password_hash, password):
                    return user_id
            return None
        
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def get_user_confirmation_status(user_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT confirmed FROM users WHERE id = %s", (user_id,))
            confirmed = cursor.fetchone()
            print(confirmed[0]==1)
            return confirmed[0] == 1 if  confirmed[0] == 1 else False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            if connection:
                connection.close()

    # def authenticate(username, password):
    #     connection = Database.connect_mysql()
    #     try:
    #         cursor = connection.cursor()
    #         # Retrieve the user's hashed password from the database
    #         cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
    #         result = cursor.fetchone()
    #
    #         if result:
    #             user_id, stored_password_hash = result
    #             # Verify the provided password against the stored hash
    #             if pbkdf2_sha256.verify(password, stored_password_hash):
    #                 return user_id
    #         return None
    #
    #     except Exception as e:
    #         print(f"An error occurred: {e}")
    #     finally:
    #         if connection:
    #             connection.close()


    @staticmethod
    def email_exists(email):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
            return cursor.fetchone()[0] > 0
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            if connection:
                connection.close()

    @staticmethod
    def username_exists(username):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
            return cursor.fetchone()[0] > 0
        except Exception as e:
            raise e
            print(f"An error occurred: {e}")
            return False
        finally:
            if connection:
                connection.close()


    @staticmethod
    def update_last_login(user_id):
        connection = None
        try:
            connection = Database.connect_mysql()
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE users SET last_login = NOW() WHERE id = %s",
                (user_id,)
            )
            connection.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def get_user_by_email(email):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user:
                user_data = {
                    'id': user[0],
                    'full_name': user[1],
                    'username': user[2],
                    'email': user[3],
                    'confirmed': user[4],  # Assuming 'confirmed' is the fifth field in your users table
                    # Add other fields as necessary
                }
                return user_data
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def confirm_user(email):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET confirmed = 1 WHERE email = %s", (email,))
            connection.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if connection:
                connection.close()


    @staticmethod
    def update_user_info(user_id, user_data):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            # Constructing the SQL query string
            sql = """UPDATE users 
                     SET full_name = %s,  phone_number = %s, 
                          role = %s,   
                          bio = %s, linkedin_url = %s, 
                         twitter_handle = %s, github_username = %s
                     WHERE id = %s"""
            # Preparing the values to be updated
            values = (
                user_data['full_name'], 
                user_data['phone_number'], 
                user_data['role'], 
                user_data['bio'], 
                user_data['linkedin_url'], 
                user_data['twitter_handle'], 
                user_data['github_username'], 
                user_id
            )
            cursor.execute(sql, values)  # Executing the query
            connection.commit()  # Committing the transaction
        except Exception as e:
            print(f"An error occurred while updating user info: {e}")
            raise e  
        finally:
            if connection:
                connection.close()  # Ensuring the connection is closed
            flash('Your information has been updated successfully.', 'success')


    @staticmethod
    def get_user_by_id(user_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            # SQL query to select user by ID. Use parameterized query for safety.
            cursor.execute("SELECT id, full_name, username, email, phone_number, gender, role, dob, city, educational_level, university, major, job_title, industry, bio, linkedin_url, twitter_handle, github_username, confirmed, is_admin FROM users WHERE id = %s", (user_id,))
            user_row = cursor.fetchone()
            if user_row:
                # Map the user row to a dictionary for easier access by column names
                user_data = {
                    'id': user_row[0],
                    'full_name': user_row[1],
                    'username': user_row[2],
                    'email': user_row[3],
                    'phone_number': user_row[4],
                    'gender': user_row[5],
                    'role': user_row[6],
                    'dob': user_row[7],
                    'city': user_row[8],
                    'educational_level': user_row[9],
                    'university': user_row[10],
                    'major': user_row[11],
                    'job_title': user_row[12],
                    'industry': user_row[13],
                    'bio': user_row[14],
                    'linkedin_url': user_row[15],
                    'twitter_handle': user_row[16],
                    'github_username': user_row[17],
                    'confirmed': user_row[18],  # Assuming 'confirmed' is part of your users table schema
                    'is_admin': user_row[19],

                }
                return user_data
            else:
                return None  # User not found
        except Exception as e:
            print(f"An error occurred while fetching user by ID: {e}")
            raise
        finally:
            if connection:
                connection.close()

    @staticmethod
    def record_password_reset_attempt(user_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            # Insert a new password reset attempt record for the user
            cursor.execute(
                "INSERT INTO password_reset_attempts (user_id, attempt_time) VALUES (%s, NOW())",
                (user_id,)
            )
            connection.commit()
        except Exception as e:
            print(f"An error occurred while recording password reset attempt: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def check_reset_attempts(user_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            # Count the number of password reset attempts in the last hour for the user
            cursor.execute("""
                SELECT COUNT(*)
                FROM password_reset_attempts
                WHERE user_id = %s AND attempt_time > DATE_SUB(NOW(), INTERVAL 1 HOUR)
            """, (user_id,))
            attempts = cursor.fetchone()[0]
            return attempts
        except Exception as e:
            print(f"An error occurred while checking password reset attempts: {e}")
            return 0
        finally:
            if connection:
                connection.close()


    @staticmethod
    def update_password(email, new_password):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            # Update the user's password in the database
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE email = %s",
                (new_password, email)
            )
            connection.commit()
        except Exception as e:
            print(f"An error occurred while updating password: {e}")
            raise e
        finally:
            if connection:
                connection.close()

    @staticmethod
    def get_user_email_by_id(user_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            if result:
                return result[0]  # Return the email address
            return None  # User not found or no email address available
        except Exception as e:
            print(f"An error occurred while fetching user email: {e}")
            return None
        finally:
            if connection:
                connection.close()


    @staticmethod
    def get_user_full_name(user_id):
        connection = None
        try:
            connection = Database.connect_mysql()  # Assuming Database.connect_mysql() method exists and establishes a connection to the database
            cursor = connection.cursor()
            # SQL query to fetch the full_name of the user based on user_id
            cursor.execute("SELECT full_name FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            if result:
                return result[0]  # Return the full_name of the user
            else:
                return None  # User not found or no full_name available
        except Exception as e:
            print(f"An error occurred while fetching user's full name: {e}")
            return None
        finally:
            if connection:
                connection.close()
