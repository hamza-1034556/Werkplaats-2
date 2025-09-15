import sqlite3

class ParentModule(object):
    def __init__(self, database_file):
        self.database_file = database_file


    def connect_to_db(self):
        con = sqlite3.connect(self.database_file)
        cur = con.cursor()
        return con, cur


    def disconnect_from_db(self, con, cur):
        cur.close()
        con.close()