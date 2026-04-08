# models/experiment.py
from datetime import datetime

class Experiment:
    def __init__(self, db):
        self.db = db

    def all(self):
        return self.db.query("SELECT id, question, metric FROM experiments ORDER BY id DESC")

    def get(self, exp_id):
        rows = self.db.query("SELECT * FROM experiments WHERE id = ?", (exp_id,))
        return rows[0] if rows else None

    def create(self, question, option_a, option_b, metric, duration_days):
        created_at = datetime.utcnow().isoformat()
        self.db.execute("""
            INSERT INTO experiments (question, option_a, option_b, metric, duration_days, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (question, option_a, option_b, metric, duration_days, created_at))
