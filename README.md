Habit‑Lab is a simple experiment‑based habit tracker built with Flask.
You create A/B experiments, log daily results, and Habit‑Lab shows which option performs better.

Features
Create custom experiments

Compare two options (A/B testing)

Log daily scores with optional notes

Automatic duration limits

View experiment history

Clean OOP architecture (models, routes, database wrapper)

SQLite backend with automatic table creation

Project Structure
Code
app.py
database.py

models/
  experiment.py
  log.py

routes/
  experiments.py
  history.py
  about.py

templates/
  index.html
  experiments.html
  new_experiment.html
  experiment_detail.html
  add_log.html
  log_limit_reached.html
  history.html
  about.html
Installation
Clone the repository:

Code
git clone https://github.com/slmanalodani/habit-lab.git
cd habit-lab
Create a virtual environment:

Code
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
Install dependencies:

Code
pip install -r requirements.txt
Run the app:

Code
python app.py
Open in your browser:

Code
http://127.0.0.1:5000
Database
Habit‑Lab uses SQLite (habitlab.db).
The database and tables are created automatically on startup.

To reset the app:

Code
rm habitlab.db
Code
http://127.0.0.1:5000
Database
Habit‑Lab uses SQLite (habitlab.db).
The database and tables are created automatically on startup.

To reset the app:

Code
rm habitlab.db
