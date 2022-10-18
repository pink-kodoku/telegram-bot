import sqlite3

# После первого запуска, закомментить self.seed_tables() в init

class API:
    def __init__(self, db_name):
        self.connect = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.connect.cursor()
        self.create_tables()
        # self.seed_tables()

    def create_tables(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "users" (
                "id"	INTEGER NOT NULL	
            );""")
        self.connect.commit()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "subscribes" (
                "user_id"	INTEGER NOT NULL,
                "category_id"	INTEGER NOT NULL,
                PRIMARY KEY("user_id","category_id")
            );""")
        self.connect.commit()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS "categories" (
                "id"	INTEGER NOT NULL,
                "name"	INTEGER NOT NULL UNIQUE,
                PRIMARY KEY("id" AUTOINCREMENT)
            );""")
        self.connect.commit()

    def is_already_seed(self):
        res = self.cursor.execute("""SELECT name FROM categories WHERE name="sports" """).fetchone()
        if res:
            return True
        else:
            return False

    def seed_tables(self):
        self.cursor.execute("""INSERT INTO categories (name)
                VALUES ("sports"),
                    ("health"),
                    ("general"),
                    ("business"),
                    ("entertainment")
                """)
        self.connect.commit()

    def unsubscribe_category(self, user_id, category_id):
        self.cursor.execute("DELETE FROM subscribes WHERE user_id = ? AND category_id = ?", (user_id, category_id,))
        return self.connect.commit()

    def add_user(self, user_id):
        self.cursor.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
        return self.connect.commit()

    def is_subscribed(self, user_id, category_id):
        res = self.cursor.execute("SELECT category_id FROM subscribes WHERE user_id = ? AND category_id = ?",
                                  (user_id, category_id,))
        return bool(len(res.fetchall()))

    def has_user(self, user_id):
        res = self.cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        return bool(len(res.fetchall()))

    def get_categories(self):
        res = self.cursor.execute("SELECT * FROM categories")
        return res.fetchall()

    def get_category(self, category_id):
        res = self.cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        return res.fetchone()

    def get_subscribes(self, user_id):
        res = self.cursor.execute(
            "SELECT category_id, name FROM subscribes INNER JOIN categories ON categories.id = subscribes.category_id WHERE user_id = ?",
            (user_id,))
        return res.fetchall()

    def subscribe_category(self, user_id, category_id):
        self.cursor.execute("INSERT INTO subscribes (user_id, category_id) VALUES (?, ?)", (user_id, category_id))
        return self.connect.commit()
