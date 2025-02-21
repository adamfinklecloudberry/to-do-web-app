"""Tests for adding tasks"""

from flask import get_flashed_messages
from sqlalchemy import text
from config import db
from flask_app import app


def test_add_task_success(client):
    """
    Test for the successful addition of a task to the task list

    - Simulates a POST request to the '/add' route with valid task data,
    including a task name and a due date
    - Verifies that the response status code is 302, indicating a
    redirect to the home page after successfully adding the task
    - Additionally checks that a success message is flashed to the user,
    confirming that the task was added successfully.
    - Uses the Flask test client to perform the request and accesses
    the flashed messages to validate the outcome

    Steps include:
    - Sending a POST request to the '/add' route with valid task data
    - Asserting that the response status code is 302 (redirect)
    - Checking that the success message "Task added successfully" is
      present in the flashed messages

    Expected outcome includes:
    The task being added to the database and the user receiving a
    success message
    """
    response = client.post("/add", data={"task": "Test Task", "due_date": "2023-12-31"})
    assert response.status_code == 302  # Check for redirect
    with app.app_context():
        assert "Task added successfully" in [
            m[1] for m in get_flashed_messages(with_categories=True)
        ]


def test_add_task_database_error(client):
    """
    Test for handling a database error when adding a task

    - Simulates a scenario where a database error occurs during the
    task addition process by dropping the 'tasks' table before sending
    a POST request to the '/add' route with valid task data
    - Verifies that the response status code is 302, indicating a
    redirect, and that an error message is flashed to the user

    Steps include:
    - Dropping the 'tasks' table to simulate a database error
    - Sending a POST request to the '/add' route with valid task data
    - Asserting that the response status code is 302 (redirect)
    - Checking that the error message "Error in adding task" is
      present in the flashed messages

    Expected outcome includes:
    The user receiving an error message indicating that there was an
    issue adding the task, and the application handling the error
    gracefully without crashing
    """
    with app.app_context():
        db.session.execute(text("DROP TABLE IF EXISTS tasks"))
        db.session
        db.session.commit()

    response = client.post("/add", data={"task": "Test Task", "due_date": "2023-12-31"})
    assert response.status_code == 302  # redirect
    with app.app_context():
        assert "Error in adding task" in [
            m[1] for m in get_flashed_messages(with_categories=True)
        ]
