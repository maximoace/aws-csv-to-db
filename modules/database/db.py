from modules.lib import pymysql
import sys

class Database:
    endpoint = "COLOQUE SEU ENDPOINT AQUI"
    user = "COLOQUE SEU USUARIO DO BANCO AQUI"
    password = "COLOQUE A SENHA DO USUARIO DO BANCO AQUI"
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