import mysql.connector
import datetime

class Database:
    @staticmethod
    def connect_mysql():
        return mysql.connector.connect(

            # host="127.0.0.1",
            # user="eduthon_mishari",
            # password="kSlEefCsgQcr",
            # database="eduthon_eduthon"

            host="127.0.0.1",
            user="root",
            password="", #password="<vvW)>yFhS[lJ2Bd'<m:UwrJh",
            database="rehaldb" # eduthondb

            # host="127.0.0.1",
            # user="root",
            # password="",
            # database="eduthon_eduthon"

        )
        return connection

class Constants:
    maxDate = datetime.datetime.now().date()
    minDate = datetime.date(1900, 1, 1)
