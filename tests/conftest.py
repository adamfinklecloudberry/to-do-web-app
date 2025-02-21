import pytest
from flask_app import app
from config import db


@pytest.fixture
def client():
    """
    Creates a test client for the Flask app

    Sets up the Flask application in testing mode and initializes
    a temporary in-memory database for the tests

    Returns:
        Flask test client: A test client that can be used to simulate
        requests to the application during testing.
    """
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SERVER_NAME'] = 'localhost'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'

    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            yield client

    with app.app_context():
        db.drop_all()