from database import Database

import db_joinrequests
from db_users import DB_Users
from db_teams import DB_Teams
from db_teammembers import DB_TeamMembers
from db_joinrequests import DB_JoinRequests

class DB_Admin:

    @staticmethod
    def get_all_users():
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            return users
        except Exception as e:
            print(f"An error occurred while fetching all users: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def update_user_role(user_id, role):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET role = %s WHERE id = %s", (role, user_id))
            connection.commit()
        except Exception as e:
            print(f"An error occurred while updating user role: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def delete_user(user_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            connection.commit()
        except Exception as e:
            print(f"An error occurred while deleting user: {e}")
        finally:
            if connection:
                connection.close()