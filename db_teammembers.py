from database import Database

class DB_TeamMembers:
    @staticmethod
    def get_team_members(team_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT users.id, users.full_name, users.role
                FROM teammembers 
                JOIN users ON teammembers.user_id = users.id 
                WHERE teammembers.team_id = %s
                """, (team_id,))
            members = cursor.fetchall()
            return members
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
        finally:
            if connection:
                connection.close()


    @staticmethod
    def add_team_member(team_id, user_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO teammembers (team_id, user_id) VALUES (%s, %s)", (team_id, user_id))
            connection.commit()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            if connection:
                connection.close()

    @staticmethod
    def remove_team_member(team_id, user_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM teammembers WHERE team_id = %s AND user_id = %s", (team_id, user_id))
            connection.commit()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            if connection:
                connection.close()

    @staticmethod
    def get_team_member_emails(team_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            # SQL query adjusted to select only the email addresses of team members
            cursor.execute("""
                SELECT users.email
                FROM teammembers
                JOIN users ON teammembers.user_id = users.id
                WHERE teammembers.team_id = %s
            """, (team_id,))
            # Fetch all matching records and extract email addresses into a list
            member_emails = [email[0] for email in cursor.fetchall()]
            return member_emails
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
        finally:
            if connection:
                connection.close()