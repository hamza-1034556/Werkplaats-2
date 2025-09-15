import sqlite3

class Redacteur:
    def __init__(self, database_file):
        self.database_file = database_file


    def connect_to_db(self):
        con = sqlite3.connect(self.database_file)
        cur = con.cursor()
        return con, cur


    def disconnect_from_db(self, con, cur):
        cur.close()
        con.close()

    def get_all_redacteurs(self):
        con, cur = self.connect_to_db()
        cur.execute("SELECT display_name, login, is_admin, user_id FROM users")
        redacteurs = cur.fetchall()
        print(redacteurs)

        self.disconnect_from_db(con, cur)


        redacteurs_list = []
        if redacteurs:
            for redacteur in redacteurs:
                redacteurs_list.append({
                    "display_name": redacteur[0],
                    "login": redacteur[1],
                    "is_admin": redacteur[2],
                    "user_id": redacteur[3]
                })

        return redacteurs_list

    def update_admin_status(self, login, is_admin):
        con, cur = self.connect_to_db()
        cur.execute("UPDATE users SET is_admin = ? WHERE login = ?", (is_admin, login))
        con.commit()
        self.disconnect_from_db(con, cur)


    def delete_redacteur(self, login):
        con, cur = self.connect_to_db()
        cur.execute("DELETE FROM users WHERE login = ?", (login,))
        con.commit()
        self.disconnect_from_db(con, cur)

    def null_redacteur(self, login):
        try:
            con, cur = self.connect_to_db()
            query = """
            UPDATE users
            SET password = NULL, date_created = NULL, is_admin = 0, login = NULL
            WHERE login = ?
            """
            cur.execute(query, (login,))
            con.commit()
        finally:
            self.disconnect_from_db(con, cur)


class AddRedacteur(Redacteur):
    def __init__(self, database_file):
        super().__init__(database_file)


    def new_redacteur(self, display_name, login, password, is_admin):
        con, cur = self.connect_to_db()
        cur.execute("""INSERT INTO users (display_name, login, password, is_admin)VALUES (?, ?, ?, ?)""",
                    (display_name, login, password, is_admin))
        con.commit()
        self.disconnect_from_db(con, cur)

