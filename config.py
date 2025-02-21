import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize the SQLAlchemy object
db = SQLAlchemy()

# Initialize the login manager
login_manager = LoginManager()


def init_app(app):
    # Set the database file based on the environment
    if app.config["TESTING"] == True:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
            os.path.dirname(__file__), "test.db"
        )
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
            os.path.dirname(__file__), "database.db"
        )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the SQLAlchemy object
    db.init_app(app)

    # Initialize the login manager
    login_manager.init_app(app)
    login_manager.login_view = "login"

    # Create the database and tables
    with app.app_context():
        db.create_all()
        print("Database initialized and tables created.")
