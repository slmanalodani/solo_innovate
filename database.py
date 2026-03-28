# database.py
import sqlite3

class Database:
    def __init__(self, path="habitlab.db"):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            metric TEXT NOT NULL,
            duration_days INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            option_used TEXT NOT NULL,
            score INTEGER NOT NULL,
            notes TEXT,
            FOREIGN KEY (experiment_id) REFERENCES experiments(id)
        )
        """)

        self.conn.commit()

    # method to run select query and return result
    def query(self, sql, params=()):
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()
    
    # method to SQL commands that change the database, such as:
    def execute(self, sql, params=()):
        self.cursor.execute(sql, params)
        self.conn.commit()
