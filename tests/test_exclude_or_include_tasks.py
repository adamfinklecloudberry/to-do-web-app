"""
Tests for including and excluding data from the task list
"""

from werkzeug.security import generate_password_hash, check_password_hash
from config import db
from flask_app import app, Task, User


def test_home_exclude_complete_tasks(client):
    """
    Tests the home route to verify that it correctly excludes complete
    tasks when the 'incomplete' query parameter is set to 'true'

    Sets up the database with a mix of complete and incomplete tasks,
    sends a GET request to the home route with the 'incomplete'
    parameter, and asserts that only incomplete tasks are present in
    the response data
    """
    # Add test data to the database with SQLAlchemy
    with app.app_context():
        # Delete all existing tasks
        db.session.query(Task).delete()

        # Add test tasks
        db.session.add(Task(name="Task 1", due_date="2023-10-01"))
        db.session.add(Task(name="Task 2", due_date="2023-10-02", complete=True))
        db.session.add(Task(name="Task 3", due_date="2023-10-03"))

        # Create a test user (assuming you have a User model)
        test_user = User(
            email="test@user.com", password=generate_password_hash("password")
        )
        db.session.add(test_user)
        db.session.commit()

    # Log in the test user
    response = client.post(
        "/login", data={"email": "test@user.com", "password": "password"}
    )

    # Check if login was successful
    assert response.status_code == 302  # Assuming a redirect after login

    # Test: Request the home route with the 'incomplete' parameter set to 'true'
    response = client.get("/?incomplete=true")

    # Assert: Check that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert: Check that the response contains only incomplete tasks
    assert b"Task 1" in response.data
    # This task is complete and should be exncluded
    assert b"Task 2" not in response.data
    assert b"Task 3" in response.data


def test_home_include_all_tasks(client):
    """
    Test the home route to verify that it includes all tasks when the
    'incomplete' query parameter is not set or set to 'false'

    This test sets up the database with a mix of complete and
    incomplete tasks, sends a GET request to the home route without the
    'incomplete' parameter, and asserts that all tasks are present in
    the response data
    """
    # Setup: Add test data to the database
    with app.app_context():
        # Create a test user (assuming you have a User model)
        test_user = User(
            email="test@user.com", password=generate_password_hash("password")
        )
        db.session.add(test_user)
        db.session.commit()

        # Add test tasks
        db.session.add(Task(name="Task 1", due_date="2023-10-01"))
        db.session.add(Task(name="Task 2", due_date="2023-10-02", complete=True))
        db.session.add(Task(name="Task 3", due_date="2023-10-03"))
        db.session.commit()

    # Log in the test user
    response = client.post(
        "/login", data={"email": "test@user.com", "password": "password"}
    )

    # Check if login was successful
    assert response.status_code == 302  # Assuming a redirect after login

    # Test: Request the home route without the 'incomplete' parameter
    response = client.get("/")

    # Assert: Check that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert: Check that the response contains all tasks
    assert b"Task 1" in response.data
    # This task is complete and should be included
    assert b"Task 2" in response.data  
    assert b"Task 3" in response.data