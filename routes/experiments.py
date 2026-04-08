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

    @bp.route("/")
    def list_experiments():
        # get all experiments from the database
        experiments = experiment_model.all()
        # show them on the experiments page
        return render_template("experiments.html", experiments=experiments)

    @bp.route("/new", methods=["GET", "POST"])
    def new_experiment():
        # if the user submitted the form
        if request.method == "POST":
            # create a new experiment using the form data
            experiment_model.create(
                request.form["question"],
                request.form["option_a"],
                request.form["option_b"],
                request.form["metric"],
                request.form["duration_days"]
            )
            # after creating, go back to the experiments list
            return redirect("/experiments")
        
        # if it's a GET request, just show the form
        return render_template("new_experiment.html")

    @bp.route("/<int:exp_id>")
    def detail(exp_id):
        # get the experiment by its ID
        experiment = experiment_model.get(exp_id)
        if not experiment:
            # if it doesn't exist, show 404
            return "Experiment not found", 404

        # how many days the experiment lasts
        duration_days = experiment[5]

        # calculate the earliest date we should include logs from
        cutoff_date = (datetime.utcnow() - timedelta(days=duration_days)).strftime("%Y-%m-%d")

        # get all logs for this experiment after the cutoff date
        logs = log_model.for_experiment(exp_id, cutoff_date)

        # option names (like "A" and "B")
        option_a = experiment[2]
        option_b = experiment[3]

        # collect scores for option A
        a_scores = [log[4] for log in logs if log[3] == option_a]
        # collect scores for option B
        b_scores = [log[4] for log in logs if log[3] == option_b]

        # calculate averages (if there are any scores)
        avg_a = sum(a_scores) / len(a_scores) if a_scores else None
        avg_b = sum(b_scores) / len(b_scores) if b_scores else None

        # figure out which option is winning
        if avg_a is not None and avg_b is not None:
            if avg_a > avg_b:
                winner = option_a
            elif avg_b > avg_a:
                winner = option_b
            else:
                winner = "Tie"
        else:
            # no winner if one side has no logs
            winner = None

        # show the experiment detail page
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
        # get the experiment
        experiment = experiment_model.get(exp_id)
        if not experiment:
            return "Experiment not found", 404

        # how many days the experiment lasts
        duration_days = experiment[5]

        # how many logs already exist
        log_count = log_model.count(exp_id)

        # if logs reached the limit (1 log per day)
        if log_count >= duration_days:
            return render_template(
                "log_limit_reached.html",
                experiment=experiment,
                duration=duration_days
            )

        # if the user submitted the log form
        if request.method == "POST":
            # create a new log entry
            log_model.create(
                exp_id,
                request.form["option_used"],
                request.form["score"],
                request.form.get("notes", "")
            )
            # go back to the experiment detail page
            return redirect(f"/experiments/{exp_id}")

        # show the add-log form
        return render_template("add_log.html", experiment=experiment)

    @bp.route("/<int:exp_id>/delete", methods=["POST"])
    def delete_experiment(exp_id):
        # delete all logs for this experiment
        db.execute("DELETE FROM logs WHERE experiment_id = ?", (exp_id,))
        # delete the experiment itself
        db.execute("DELETE FROM experiments WHERE id = ?", (exp_id,))
        # go back to the list
        return redirect("/experiments")

    # register the blueprint so Flask knows about these routes
    app.register_blueprint(bp, url_prefix="/experiments")
