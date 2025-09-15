import sqlite3

class ActiveRedacteur:
    def __init__(self, database_file):
        self.database_file = database_file

    def connect_to_db(self):
        con = sqlite3.connect(self.database_file)
        cur = con.cursor()
        return con, cur

    def disconnect_from_db(self, con, cur):
        cur.close()
        con.close()

    def get_active_redacteur(self, login):
        con, cur = self.connect_to_db()
        cur.execute("SELECT display_name, login, is_admin FROM users WHERE login = ?", (login,))
        redacteur_data = cur.fetchone()
        self.disconnect_from_db(con, cur)
        if redacteur_data:
            return {
                "display_name": redacteur_data[0],
                "login": redacteur_data[1],
                "is_admin": redacteur_data[2]
            }
        return None

    def update_redacteur(self, login, display_name, new_login, password, is_admin):
        con, cur = self.connect_to_db()
        if password:
            cur.execute("UPDATE users SET display_name=?, login=?, password=?, is_admin=? WHERE login=?",
                        (display_name, new_login, password, is_admin, login))
        else:
            cur.execute("UPDATE users SET display_name=?, login=?, is_admin=? WHERE login=?",
                        (display_name, new_login, is_admin, login))
        con.commit()
        self.disconnect_from_db(con, cur)
