import sqlite3

from lib.model.database import Database

class User:
    def __init__(self):
        self.database = Database('databases/database.db')
        self.cursor, self.con = self.database.connect_db()

    def show_user(self, login, password):
        self.cursor.row_factory = sqlite3.Row
        result = self.cursor.execute('SELECT * FROM users WHERE login=? AND password = ?', (login, password)).fetchone()

        if result:
            return dict(result)
        return None

    def show_username(self, user_id):
        self.cursor.row_factory = sqlite3.Row
        result = self.cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,)).fetchone()
        return result







