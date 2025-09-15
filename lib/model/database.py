import sqlite3

class Database:
    def __init__(self, path):
        self.path = path

    def connect_db(self):
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        return cur, con