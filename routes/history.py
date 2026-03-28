# routes/history.py
from flask import Blueprint, render_template

def init_history_routes(app, db):
    bp = Blueprint("history", __name__)

    @bp.route("/history")
    def history():
        rows = db.query("""
            SELECT experiments.id, experiments.question,
                   logs.date, logs.option_used, logs.score, logs.notes
            FROM logs
            JOIN experiments ON logs.experiment_id = experiments.id
            ORDER BY experiments.id, logs.date DESC
        """)

        # Group logs by experiment
        history = {}
        for exp_id, question, date, option_used, score, notes in rows:
            if exp_id not in history:
                history[exp_id] = {
                    "question": question,
                    "logs": []
                }
            history[exp_id]["logs"].append((date, option_used, score, notes))

        return render_template("history.html", history=history)

    app.register_blueprint(bp)
