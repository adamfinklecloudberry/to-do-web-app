"""
A To-Do app

Allows users to manage a list of tasks

Users can add, complete, delete, and view tasks.

Stores tasks in a SQLite database and provides both a web interface and
a JSON API for task management
"""

from flask import Flask
from config import init_app
from routes.home import home_bp
from routes.authentication import authentication_bp
from routes.tasks import tasks_bp
from routes.api import api_bp


app = Flask(__name__)

# Initialize the app with the database and login manager
init_app(app)

# Register the blueprint
app.register_blueprint(home_bp)
app.register_blueprint(authentication_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(api_bp)


if __name__ == "__main__":
    app.run(debug=True)
