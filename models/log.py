# models/log.py
from datetime import datetime

class Log:
    def __init__(self, db):
        self.db = db

    def for_experiment(self, exp_id, cutoff_date):
        return self.db.query("""
            SELECT id, experiment_id, date, option_used, score, notes
            FROM logs
            WHERE experiment_id = ?
            AND date >= ?
            ORDER BY id DESC
        """, (exp_id, cutoff_date))

    def count(self, exp_id):
        return self.db.query("SELECT COUNT(*) FROM logs WHERE experiment_id = ?", (exp_id,))[0][0]

    def create(self, exp_id, option_used, score, notes):
        date = datetime.utcnow().strftime("%Y-%m-%d")
        self.db.execute("""
            INSERT INTO logs (experiment_id, date, option_used, score, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (exp_id, date, option_used, score, notes))
