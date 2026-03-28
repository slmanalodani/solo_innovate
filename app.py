from flask import Flask, render_template
from database import Database

# Route initializers
from routes.experiments import init_routes as init_experiment_routes
from routes.history import init_history_routes

app = Flask(__name__)

# Create a single shared database instance
db = Database()

# Register route modules
init_experiment_routes(app, db)
init_history_routes(app, db)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")




if __name__ == "__main__":
    app.run(debug=True)
