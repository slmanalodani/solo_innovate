# routes/experiments.py
from flask import Blueprint, render_template, request, redirect
from models.experiment import Experiment
from models.log import Log
from datetime import datetime, timedelta

# making a blueprint for all experiment-related routes
bp = Blueprint("experiments", __name__)

def init_routes(app, db):
    # create model objects so we can talk to the database
    experiment_model = Experiment(db)
    log_model = Log(db)

    # -------------------------------
    # AI SUMMARY FUNCTION
    # -------------------------------
    import requests as req

    OLLAMA_URL = "http://localhost:11434/api/generate"
    MODEL_NAME = "habitlab"

    def generate_ai_summary(avg_a, avg_b, count_a, count_b, winner):
        avg_a_val = round(avg_a, 2) if avg_a is not None else "no data"
        avg_b_val = round(avg_b, 2) if avg_b is not None else "no data"
        winner_val = winner if winner else "no winner yet"

        prompt = (
            f"experiment:\n"
            f"option_a_avg: {avg_a_val}\n"
            f"option_b_avg: {avg_b_val}\n"
            f"option_a_uses: {count_a}\n"
            f"option_b_uses: {count_b}\n"
            f"winner: {winner_val}"
        )

        response = req.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }, timeout=30)

        raw = response.json().get("response", "").strip()

        # Extract only the clean summary — stop when it starts repeating data
        import re as _re
        # Split into sentences
        sentences = _re.split(r'(?<=[.!?])\s+', raw)
        clean = []
        for s in sentences:
            # Stop if the sentence looks like raw data output
            if any(x in s.lower() for x in [
                'option_a', 'option_b', 'strategy_a', 'strategy_b',
                'metric:', 'duration:', 'goal:', '=', 'rate how',
                'where 1', '1-5', '1/4', '2/4', '3/4', '4/4'
            ]):
                break
            clean.append(s)
            if len(clean) >= 3:  # Max 3 sentences
                break

        return ' '.join(clean).strip() if clean else "Not enough data to summarize yet."
    # -------------------------------


    @bp.route("/")
    def list_experiments():
        experiments = experiment_model.all()
        return render_template("experiments.html", experiments=experiments)

    @bp.route("/new", methods=["GET", "POST"])
    def new_experiment():
        if request.method == "POST":
            experiment_model.create(
                request.form["question"],
                request.form["option_a"],
                request.form["option_b"],
                request.form["metric"],
                request.form["duration_days"]
            )
            return redirect("/experiments")
        
        return render_template("new_experiment.html")

    @bp.route("/<int:exp_id>")
    def detail(exp_id):
        experiment = experiment_model.get(exp_id)
        if not experiment:
            return "Experiment not found", 404

        duration_days = experiment[5]
        cutoff_date = (datetime.utcnow() - timedelta(days=duration_days)).strftime("%Y-%m-%d")
        logs = log_model.for_experiment(exp_id, cutoff_date)

        option_a = experiment[2]
        option_b = experiment[3]

        a_scores = [log[4] for log in logs if log[3] == option_a]
        b_scores = [log[4] for log in logs if log[3] == option_b]

        avg_a = sum(a_scores) / len(a_scores) if a_scores else None
        avg_b = sum(b_scores) / len(b_scores) if b_scores else None

        if avg_a is not None and avg_b is not None:
            if avg_a > avg_b:
                winner = option_a
            elif avg_b > avg_a:
                winner = option_b
            else:
                winner = "Tie"
        else:
            winner = None

        # -------------------------------
        # AI SUMMARY LOGIC
        # -------------------------------
        count_a = sum(1 for log in logs if log[3] == option_a)
        count_b = sum(1 for log in logs if log[3] == option_b)

        # Only call AI if there is actual data to summarize
        if avg_a is not None or avg_b is not None:
            try:
                summary_text = generate_ai_summary(avg_a, avg_b, count_a, count_b, winner)
            except Exception:
                summary_text = "Summary unavailable right now."
        else:
            summary_text = ""
        # -------------------------------

        return render_template(
            "experiment_detail.html",
            experiment=experiment,
            logs=logs,
            avg_a=avg_a,
            avg_b=avg_b,
            winner=winner,
            summary_text=summary_text  # <-- pass summary to template
        )

    @bp.route("/<int:exp_id>/log", methods=["GET", "POST"])
    def add_log(exp_id):
        experiment = experiment_model.get(exp_id)
        if not experiment:
            return "Experiment not found", 404

        duration_days = experiment[5]
        log_count = log_model.count(exp_id)

        if log_count >= duration_days:
            return render_template(
                "log_limit_reached.html",
                experiment=experiment,
                duration=duration_days
            )

        if request.method == "POST":
            log_model.create(
                exp_id,
                request.form["option_used"],
                request.form["score"],
                request.form.get("notes", "")
            )
            return redirect(f"/experiments/{exp_id}")

        return render_template("add_log.html", experiment=experiment)

    @bp.route("/<int:exp_id>/delete", methods=["POST"])
    def delete_experiment(exp_id):
        db.execute("DELETE FROM logs WHERE experiment_id = ?", (exp_id,))
        db.execute("DELETE FROM experiments WHERE id = ?", (exp_id,))
        return redirect("/experiments")

    app.register_blueprint(bp, url_prefix="/experiments")
