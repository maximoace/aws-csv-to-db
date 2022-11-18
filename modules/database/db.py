from modules.lib import pymysql
import sys

class Database:
    endpoint = "mariadb-instance-1.cfxgu4o6csfw.us-east-1.rds.amazonaws.com"
    user = "admin"
    password = "aws-serveless"
    database = "edesoft_db"

    def __init__(self) -> None:
        try:
            self.con = pymysql.connect(
                host = self.endpoint,
                user = self.user,
                password = self.password,
                database = self.database,
                autocommit = True
            )
        except pymysql.Error as e:
            print(f"Error connecting to the database: {e}")
            sys.exit(1)

    def get_cursor(self):
        return self.con.cursor()