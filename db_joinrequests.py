from database import Database

class DB_JoinRequests:
    @staticmethod
    def create_join_request(request_data):
        connection = None
        try:
            connection = Database.connect_mysql()
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO joinrequests (team_id, user_id) VALUES (%s, %s)",
                (request_data['team_id'], request_data['user_id']))
            connection.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"An error occurred: {e}")
            raise e
        finally:
            if connection:
                connection.close()


    @staticmethod
    def get_join_requests_for_team(team_id):
        connection = None
        try:
            connection = Database.connect_mysql()
            cursor = connection.cursor()
            cursor.execute("""
            SELECT joinrequests.request_id, joinrequests.team_id, joinrequests.user_id, 
                   users.full_name, users.email, users.role, users.phone_number
            FROM joinrequests
            JOIN users ON joinrequests.user_id = users.id
            WHERE joinrequests.team_id = %s AND joinrequests.status = 'PENDING'
        """, (team_id,))
            requests = cursor.fetchall()
            return requests
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def accept_join_request(request_id, team_id, user_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()

            # Check if the user is the team leader
            cursor.execute("SELECT created_by FROM teams WHERE team_id = %s", (team_id,))
            result = cursor.fetchone()
            if not result or result[0] != user_id:
                return False

            # Update join request status
            cursor.execute("UPDATE joinrequests SET status = 'ACCEPTED', handled_by = %s WHERE request_id = %s",
                           (user_id, request_id))

            # Add user to team members
            cursor.execute("SELECT user_id FROM joinrequests WHERE request_id = %s", (request_id,))
            member_user_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO teammembers (team_id, user_id) VALUES (%s, %s)", (team_id, member_user_id))

            connection.commit()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            if connection:
                connection.close()

    @staticmethod
    def reject_join_request(request_id, team_id, user_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()

            # Check if the user is the team leader
            cursor.execute("SELECT created_by FROM teams WHERE team_id = %s", (team_id,))
            result = cursor.fetchone()
            if not result or result[0] != user_id:
                return False

            # Update join request status
            cursor.execute("UPDATE joinrequests SET status = 'REJECTED', handled_by = %s WHERE request_id = %s",
                           (user_id, request_id))

            connection.commit()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            if connection:
                connection.close()

    @staticmethod
    def has_pending_request(user_id, team_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM joinrequests WHERE user_id = %s AND team_id = %s AND status = 'PENDING'",
                           (user_id, team_id))
            return cursor.fetchone() is not None
        finally:
            if connection:
                connection.close()

    @staticmethod
    def get_user_pending_requests(user_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT team_id FROM joinrequests WHERE user_id = %s AND status = 'PENDING'", (user_id,))
            pending_requests = cursor.fetchall()
            return [request[0] for request in pending_requests]  # Extract team IDs
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
        finally:
            if connection:
                connection.close()

    @staticmethod
    def has_pending_request(user_id):
        connection = Database.connect_mysql()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM joinrequests WHERE user_id = %s AND status = 'PENDING'", (user_id,))
            return cursor.fetchone()[0] > 0
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            if connection:
                connection.close()

    @staticmethod
    def cancel_join_request(user_id, team_id):
        connection = None
        try:
            connection = Database.connect_mysql()
            cursor = connection.cursor()
            query = "DELETE FROM joinrequests WHERE user_id = %s AND team_id = %s"
            cursor.execute(query, (user_id, team_id))
            connection.commit()
            return True
        except Exception as e:
            print(f"An error occurred(i am cacnel join request): {e}")
            return False
        finally:
            if connection:
                connection.close()


    @staticmethod
    def get_requester_id(request_id):
        connection = None
        try:
            connection = Database.connect_mysql()  # Assuming you have a Database class to handle connection
            cursor = connection.cursor()
            # SQL query to fetch the user_id of the requester based on request_id
            cursor.execute("SELECT user_id FROM joinrequests WHERE request_id = %s", (request_id,))
            result = cursor.fetchone()
            if result:
                return result[0]  # Return the user_id of the requester
            else:
                return None  # No such request found
        except Exception as e:
            print(f"An error occurred while fetching requester ID: {e}")
            return None
        finally:
            if connection:
                connection.close()