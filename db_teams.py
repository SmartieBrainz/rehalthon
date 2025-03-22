from database import Database
class DB_Teams:
    # @staticmethod
    # def create_team(team_data):
    #     connection = None
    #     try:
    #         connection = Database.connect_mysql()
    #         cursor = connection.cursor()
    #         cursor.execute(
    #             "INSERT INTO teams (team_name, created_by) VALUES (%s, %s)",
    #             (team_data['team_name'], team_data['created_by']))
    #         connection.commit()
    #         return cursor.lastrowid
    #     except Exception as e:
    #         print(f"An error occurred: {e}")
    #     finally:
    #         if connection:
    #             connection.close()

    @staticmethod
    def create_team(team_data):
        connection = None
        try:
            connection = Database.connect_mysql()
            cursor = connection.cursor()

            # Step 1: Create the team
            cursor.execute(
                "INSERT INTO teams (team_name, created_by) VALUES (%s, %s)",
                (team_data['team_name'], team_data['created_by']))
            team_id = cursor.lastrowid  # Retrieve the ID of the newly created team

            # Step 2: Add the creator as a member of the team
            cursor.execute(
                "INSERT INTO teammembers (team_id, user_id) VALUES (%s, %s)",
                (team_id, team_data['created_by']))

            connection.commit()
            return team_id
        except Exception as e:
            print(f"An error occurred: {e}")
            raise e
            # Optionally, you might want to handle the exception differently or re-raise it
            return None
        finally:
            if connection:
                connection.close()

    @staticmethod
    def is_leader(team_id, user_id):
        connection = None
        try:
            connection = Database.connect_mysql()
            cursor = connection.cursor()
            cursor.execute("SELECT created_by FROM teams WHERE team_id = %s", (team_id,))
            result = cursor.fetchone()
            return result and result[0] == user_id
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def get_leader(team_id):
        connection = None
        try:
            connection = Database.connect_mysql()
            cursor = connection.cursor()
            # Query to get the user_id of the team leader
            cursor.execute("SELECT created_by FROM teams WHERE team_id = %s", (team_id,))
            result = cursor.fetchone()
            # Return the user_id of the team leader if a record is found
            return result[0] if result else None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            if connection:
                connection.close()



    @staticmethod
    def get_team_name(team_id):
        connection = None
        try:
            connection = Database.connect_mysql()
            cursor = connection.cursor()
            # Query to get the user_id of the team leader
            cursor.execute("SELECT team_name FROM teams WHERE team_id = %s", (team_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            if connection:
                connection.close()
    
    @staticmethod
    def get_team_leader_by_team_id(team_id):
        connection = None
        try:
            connection = Database.connect_mysql()
            cursor = connection.cursor()
            # Query to select the team leader based on the 'created_by' field in the 'teams' table
            sql = """
                SELECT users.id, users.full_name, users.username, users.email
                FROM users
                INNER JOIN teams ON users.id = teams.created_by
                WHERE teams.team_id = %s
            """
            cursor.execute(sql, (team_id,))
            leader = cursor.fetchone()
            return leader
        except Exception as e:
            print(f"An error occurred while retrieving the team leader: {e}")
            return None
        finally:
            if connection:
                connection.close()




    @staticmethod
    def remove_member(team_id, user_id, leader_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()

            # Check if the user is the team leader
            cursor.execute("SELECT created_by FROM teams WHERE team_id = %s", (team_id,))
            result = cursor.fetchone()
            if not result or result[0] != leader_id:
                return False

            # Remove user from team members
            cursor.execute("DELETE FROM teammembers WHERE team_id = %s AND user_id = %s", (team_id, user_id))

            connection.commit()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            if connection:
                connection.close()


    # @staticmethod
    # def get_team_members(team_id):
    #     connection = Database.connect_mysql()
    #     try:
    #         cursor = connection.cursor()
    #         cursor.execute("""
    #                SELECT users.id, users.username
    #                FROM teammembers
    #                JOIN users ON teammembers.user_id = users.id
    #                WHERE teammembers.team_id = %s
    #                """, (team_id,))
    #         members = cursor.fetchall()
    #         return members
    #     except Exception as e:
    #         print(f"An error occurred: {e}")
    #         return []
    #     finally:
    #         if connection:
    #             connection.close()

    @staticmethod
    def get_team_members(team_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            # Adjust the SQL query to select the role as well
            cursor.execute("""
                   SELECT users.id, users.username, users.role, users.full_name, users.email, users.phone_number
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
    def get_all_teams_with_leaders():
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                        SELECT teams.team_id, teams.team_name, users.username as leader_name
                        FROM teams
                        JOIN users ON teams.created_by = users.id
                    """)
            teams = cursor.fetchall()
            return teams
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
        finally:
            if connection:
                connection.close()

    
    
    # @staticmethod
    # def delete_team(team_id):
    #     connection = Database.connect_mysql()
    #     try:
    #         cursor = connection.cursor()
    #         # Delete related data first (members, join requests, etc.)
    #         cursor.execute("DELETE FROM teammembers WHERE team_id = %s", (team_id,))
    #         cursor.execute("DELETE FROM joinrequests WHERE team_id = %s", (team_id,))
    #         # Delete the team
    #         cursor.execute("DELETE FROM teams WHERE team_id = %s", (team_id,))
    #         connection.commit()
    #         return True
    #     except Exception as e:
    #         print(f"An error occurred: {e}")
    #         connection.rollback()
    #     finally:
    #         if connection:
    #             connection.close()
                


    @staticmethod
    def delete_team(team_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            connection.start_transaction()  # Explicitly start a transaction (for MySQL)

            # Perform delete operations
            cursor.execute("DELETE FROM teammembers WHERE team_id = %s", (team_id,))
            cursor.execute("DELETE FROM joinrequests WHERE team_id = %s", (team_id,))
            cursor.execute("DELETE FROM teams WHERE team_id = %s", (team_id,))

            connection.commit()  # Commit if all operations are successful
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            connection.rollback()  # Rollback changes if an exception occurs
            return False
        finally:
            if connection:
                connection.close()



    @staticmethod
    def get_user_team(user_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT t.team_id, t.team_name
                FROM teams t
                JOIN teammembers tm ON t.team_id = tm.team_id
                WHERE tm.user_id = %s
                LIMIT 1
            """, (user_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            if connection:
                connection.close()

    @staticmethod
    def user_is_leader(user_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM teams WHERE created_by = %s", (user_id,))
            return cursor.fetchone()[0] > 0
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            if connection:
                connection.close()

    @staticmethod
    def is_user_member_of_team(user_id, team_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM teammembers WHERE user_id = %s AND team_id = %s", (user_id, team_id))
            return cursor.fetchone()[0] > 0
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            if connection:
                connection.close()

    @staticmethod
    def is_user_member_of_team(user_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM teammembers WHERE user_id = %s", (user_id,))
            return cursor.fetchone()[0] > 0
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            if connection:
                connection.close()

    @staticmethod
    def get_all_teams():
        connection = None
        try:
            connection = Database.connect_mysql()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM teams")
            teams = cursor.fetchall()
            return teams
        except Exception as e:
            print(f"An error occurred: {e}")
            raise e
        finally:
            if connection:
                connection.close()

    @staticmethod
    def get_all_teams_dict():
        connection = None
        try:
            connection = Database.connect_mysql()
            cursor = connection.cursor(dictionary=True)  # Make sure to fetch results as dictionaries
            cursor.execute("SELECT * FROM teams")
            teams = cursor.fetchall()
            return teams
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def remove_member(team_id, user_id, acting_user_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()

            # Check if acting user is the team leader or the member themselves
            cursor.execute("SELECT created_by FROM teams WHERE team_id = %s", (team_id,))
            result = cursor.fetchone()
            if not result:
                return "Team not found."

            is_leader = result[0] == acting_user_id
            is_self_removal = user_id == acting_user_id

            if not (is_leader or is_self_removal):
                return "Unauthorized access."

            # Remove user from team members
            cursor.execute("DELETE FROM teammembers WHERE team_id = %s AND user_id = %s", (team_id, user_id))
            if cursor.rowcount == 0:
                return "Member not found."

            connection.commit()
            return "Success"
        except Exception as e:
            print(f"An error occurred: {e}")
            return "Error"
        finally:
            if connection:
                connection.close()
    @staticmethod
    def get_team_name_by_requester_id(requester_id):
        connection = None
        try:
            connection = Database.connect_mysql()
            cursor = connection.cursor()
            query = """
                SELECT t.team_name
                FROM joinrequests jr
                JOIN teams t ON jr.team_id = t.team_id
                WHERE jr.user_id = %s
            """
            cursor.execute(query, (requester_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            if connection:
                connection.close()

    @staticmethod
    def get_team_id_by_requester_id(requester_id):
        connection = None
        try:
            connection = Database.connect_mysql()
            cursor = connection.cursor()
            query = """
                    SELECT t.team_id
                    FROM joinrequests jr
                    JOIN teams t ON jr.team_id = t.team_id
                    WHERE jr.user_id = %s
                """
            cursor.execute(query, (requester_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"An error occurred on query get team id: {e}")
            return None
        finally:
            if connection:
                connection.close()

    @staticmethod
    def get_team_member_count(team_id):
        connection = None
        try:
            connection = Database.connect_mysql()
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM teammembers WHERE team_id = %s", (team_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            if connection:
                connection.close()


    @staticmethod
    def update_project_upload_status(team_id, upload_status):
        connection = None
        try:
            connection = Database.connect_mysql()
            cursor = connection.cursor()
            cursor.execute("UPDATE teams SET is_project_uploaded = %s WHERE team_id = %s", (1 if upload_status else 0, team_id))
            connection.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if connection:
                connection.close()


    @staticmethod
    def is_project_uploaded(team_id):
        connection = None
        try:
            connection = Database.connect_mysql()
            cursor = connection.cursor()
            cursor.execute("SELECT is_project_uploaded FROM teams WHERE team_id = %s", (team_id,))
            result = cursor.fetchone()
            return result[0] if result else False
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if connection:
                connection.close()
                
                
    
    # @staticmethod
    # def delete_team(team_id):
    #     connection = Database.connect_mysql()
    #     try:
    #         cursor = connection.cursor()
    #         # Delete the team members first to maintain referential integrity
    #         cursor.execute("DELETE FROM teammembers WHERE team_id = %s", (team_id,))
    #         # Then, delete the team itself
    #         cursor.execute("DELETE FROM teams WHERE team_id = %s", (team_id,))
    #         connection.commit()
    #         return True  # Indicate success
    #     except Exception as e:
    #         print(f"An error occurred: {e}")
    #         connection.rollback()  # Rollback in case of any failure
    #         return False  # Indicate failure
    #     finally:
    #         if connection:
    #             connection.close()
