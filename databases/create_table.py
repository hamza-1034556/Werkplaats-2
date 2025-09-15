import sqlite3


def create_new_table(database_file):
    #Connect with database
    con = sqlite3.connect(database_file)
    cur = con.cursor()

    # SQL query
    cur.execute("""
            CREATE TABLE IF NOT EXISTS new_questions (
                question_id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                prompts_id INTEGER,
                user_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

    print("New table created successfully.")

    #Close connection
    con.commit()
    con.close()

#   Execute function with database
create_new_table('database.db')
