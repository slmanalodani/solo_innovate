Habit‑Lab is a simple experiment‑based habit tracker built with Flask. It lets you create A/B experiments, log daily results, and see which option performs better over time. The goal is to help you make better decisions about your habits using real data instead of guesswork.

Features:

Create custom experiments

Compare two options (A/B testing)

Log daily scores with optional notes

Automatic duration limits based on the experiment length

View full experiment history

Organized code structure using models, routes, and a database wrapper

SQLite backend with automatic table creation


Installation:

Clone the repository: git clone https://github.com/slmanalodani/solo_innovate.git

Enter the folder: cd habit-lab

Create a virtual environment

Install dependencies with pip install -r requirements.txt

Run the app using python app.py

Open http://127.0.0.1:5000 in your browser

Database:
Habit‑Lab uses a SQLite database named habitlab.db. The database and tables are created automatically when the app starts. To reset the app, delete the habitlab.db file.
