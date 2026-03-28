# routes/experiments.py
from flask import Blueprint, render_template, request, redirect
from models.experiment import Experiment
from models.log import Log
from datetime import datetime, timedelta

bp = Blueprint("experiments", __name__)

def init_routes(app, db):
    experiment_model = Experiment(db)
    log_model = Log(db)

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

        return render_template(
            "experiment_detail.html",
            experiment=experiment,
            logs=logs,
            avg_a=avg_a,
            avg_b=avg_b,
            winner=winner
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

    # Register AFTER all routes are defined
    app.register_blueprint(bp, url_prefix="/experiments")
