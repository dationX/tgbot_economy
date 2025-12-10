import sqlite3


class DB_manager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.db = sqlite3.connect(f"{self.db_name}.db", check_same_thread=False)

    def create_table(self):
        self.db.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER NOT NULL UNIQUE, requests_text INTEGER NOT NULL, requests_image INTEGER NOT NULL, gpt_chat INTEGER)")
        self.db.commit()

    def add_user(self, user_id):
        parameters = (user_id, 0, 0, 0)

        try:
            self.db.execute(f"INSERT INTO users VALUES (?, ?, ?, ?)", parameters)
            self.db.commit()
        except:
            pass

    def add_request(self, where, user_id):
        self.db.execute(f"UPDATE users SET requests_{where}=requests_{where}+1 WHERE user_id=?", (user_id,))
        self.db.commit()

    def chat_gpt_session(self, user_id):
        cur = self.db.cursor()
        cur.execute(f"""
SELECT gpt_chat FROM users
WHERE user_id = {user_id};
""")
        data = cur.fetchall()
        if data[0][0] == 0:
            cur.execute(f"UPDATE users SET gpt_chat=1 WHERE user_id = {user_id}")
        else:
            cur.execute(f"UPDATE users SET gpt_chat=0 WHERE user_id = {user_id}")

        self.db.commit()
