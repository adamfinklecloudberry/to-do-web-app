"""
Tests for flask_app

Contains unit tests for the bulk addition of tasks, ensuring that the
application handles various scenarios correctly, such as successful
additions, invalid data formats, and missing fields in task entries

Creates a temporary in-memory database for testing purposes, ensuring
that the tests do not affect the production database
"""

import os
import tempfile
import json
import pytest
from flask import Flask, flash, get_flashed_messages, url_for
import sqlite3
from flask_app import app, db, init_db, Task
from sqlalchemy import text


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

    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            yield client

    with app.app_context():
        db.drop_all()


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

        db.session.commit()

    # Test: Request the home route with the 'incomplete' parameter set to 'true'
    response = client.get("/?incomplete=true")

    # Assert: Check that the response status code is 200 (OK)
    assert response.status_code == 200

    # Debug: Print the response data to inspect the HTML output

    # Assert: Check that the response contains only incomplete tasks
    assert b"Task 1" in response.data
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
        db.session.add(Task(name="Task 1", due_date="2023-10-01"))
        db.session.add(Task(name="Task 2", due_date="2023-10-02"))
        db.session.add(Task(name="Task 3", due_date="2023-10-03"))
        db.session.commit()

    # Test: Request the home route without the 'incomplete' parameter
    response = client.get("/")

    # Assert: Check that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert: Check that the response contains all tasks
    assert b"Task 1" in response.data
    # This task is complete and should be included
    assert b"Task 2" in response.data
    assert b"Task 3" in response.data


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


def test_edit_get(client):
    """
    Test the GET request to the edit route

    Verifies that the GET request to the `/edit/<int:task_id>` route
    returns a successful response with the correct HTML content

    Checks that the response status code is 200 (OK) and that the
    response data contains the expected text 'Edit the Name of This
    Task'.
    """
    with app.app_context():
        db.session.add(Task(name="Task 1", due_date="2023-10-01"))
        db.session.commit()
    response = client.get("/edit/1")
    assert response.status_code == 200
    assert b"Edit the Name of This Task" in response.data


def test_edit_task_success(client):
    """
    Check whether editing a task works

    Verifies that the POST request to the `/edit/<int:task_id>` route
    successfully updates a task in the database

    Performs the following steps:
    1. Inserts a new task into the database with specific values
    2. Sends a POST request to the edit route with updated task data
    3. Checks that the response status code is 302 (Redirect) and that the
       redirect location is correct
    4. Verifies that the task has been updated in the database by
       checking the `name` field of the task with `id = 1`
    """
    with app.app_context():
        # Step 1: Insert a new task into the database
        name, due_date, complete = "walk", "2024-04-19", False
        new_task = Task(name=name, due_date=due_date, complete=complete)
        db.session.add(new_task)
        db.session.commit()

    # Step 2: Send a POST request to the edit route with updated task data
    response = client.post("/edit/1", data={"task": "Updated Task"})

    # Step 3: Check that the response status code is 302 (Redirect)
    assert response.status_code == 302  # Redirect to home
    assert response.location == url_for("home", _external=False)

    # Step 4: Verify the task has been updated in the database
    updated_task = Task.query.get(1)  # Fetch the task with id = 1
    assert updated_task.name == "Updated Task"


def test_bulk_add_tasks_success(client):
    """
    Tests successful bulk addition of tasks

    Verifies that the application correctly handles a request to bulk
    add multiple tasks

    Sends a valid list of task dictionaries to the '/bulk_add' endpoint,
    checks that the response status code is 201 (Created) and that
    the response message indicates success, and verifies that the
    count of added tasks matches the number of tasks sent

    Args:
        client: The Flask test client used to make requests to the
                application.
    """
    tasks = [
        {"name": "Task 1", "due_date": "2023-10-01", "complete": False},
        {"name": "Task 2", "due_date": "2023-10-02", "complete": False},
    ]
    response = client.post(
        "/bulk_add",
        data=json.dumps(tasks),
        content_type="application/json",
    )
    assert response.status_code == 201
    assert response.json["message"] == "Tasks added successfully"
    assert response.json["count"] == 2


def insert_task(name: str, due_date: str, complete: bool) -> None:
    """Helper function to insert data for tests"""
    # Create a new Task instance
    new_task = Task(name=name, due_date=due_date, complete=complete)

    # Add the new task to the session and commit
    db.session.add(new_task)
    db.session.commit()


def get_task(task_id: int) -> None:
    """
    Helper function for finding tasks for tests

    Returns:
        The task in the database with this id
    """
    return Task.query.get(task_id)


def test_complete_task(client):
    """
    Tests whether the task is marked as complete in the database

    - Sets up a new task and sends a POST request to mark the task as
      complete
    - Asserts that the response is correct
    - Asserts that the updated task data matches the expected values
    """
    name, due_date, complete = "Test task", "2023-01-01", False
    insert_task(name, due_date, complete)
    response = client.post("/complete/1")
    assert response.status_code == 302  # redirect

    task = get_task(1)
    task_id = 1
    complete = 1
    assert task.name == "Test task"
    assert task.due_date == "2023-01-01"
    assert task.complete == True


def test_delete_task(client):
    """
    Tests whether a task can be deleted

    Inserts a task and then deletes it, checking for correct status
    code and that the task is gone
    """
    task_id, name, due_date, complete = 1, "Test task", "2023-01-01", False
    insert_task(name, due_date, complete)
    response = client.get(f"/delete/{task_id}")
    assert response.status_code == 302  # redirect
    assert get_task(task_id) is None


def test_delete_all_tasks(client):
    """
    Tests whether all tasks can be deleted

    Inserts two task and then deletes it, checking for correct status
    code and that the tasks are gone
    """
    name, due_date, complete = "Test task 1", "2023-01-01", False
    other_name, other_due_date, other_complete = "Test task 2", "2023-01-02", False
    insert_task(name, due_date, complete)
    insert_task(name, due_date, complete)
    response = client.post("/delete_all")
    assert response.status_code == 302  # redirect
    assert get_task(1) is None
    assert get_task(2) is None


def test_get_tasks(client):
    """
    Tests whether the api to retrieve all tasks as a JSON works

    Creates the data for two tasks, inserts them into the test
    database, requests them by api, and checks that the response
    code and json are correct
    """
    name, due_date, complete = "Test task 1", "2023-01-01", False
    other_name, other_due_date, other_complete = "Test task 2", "2023-01-02", False
    insert_task(name, due_date, complete)
    insert_task(name, due_date, complete)
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.json == [
        {"id": 1, "name": name, "due_date": due_date, "complete": complete},
        {"id": 2, "name": name, "due_date": due_date, "complete": complete},
    ]


def test_bulk_add_tasks_invalid_format(client):
    """
    Tests bulk addition with non-list data format, which is invalid

    Checks the application's response when the input data is not in the
    expected list format

    Sends a single task dictionary instead of a list and verifies that
    the response status code is 400 (Bad Request) and that the error
    message indicates the invalid data format

    Args:
        client: The Flask test client used to make requests to the
                application.
    """
    invalid_data = {"name": "Task 1", "due_date": "2023-10-01"}
    response = client.post(
        "/bulk_add",
        data=json.dumps(invalid_data),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["error"] == "Invalid data format.  Expected a list of tasks."


def test_bulk_add_tasks_missing_fields(client):
    """
    Tests bulk addition with missing fields in tasks

    Verifies that the application correctly handles cases where tasks
    are missing required fields

    Sends task entries with missing 'name' and 'due_date' fields and
    checks that the response status code is 400 (Bad Request) and that
    the error messages specify which fields are missing

    Args:
        client: The Flask test client used to make requests to the
                application.
    """
    task_with_missing_name = [{"due_date": "2023-10-02"}]
    task_with_missing_due_date = [{"name": "Task 1"}]

    response = client.post(
        "/bulk_add",
        data=json.dumps(task_with_missing_name),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["error"] == (
        "Each task must have a name and due_date.  "
        "The name was missing and due_date was 2023-10-02."
    )

    response = client.post(
        "/bulk_add",
        data=json.dumps(task_with_missing_due_date),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["error"] == (
        "Each task must have a name and due_date.  "
        "The name was Task 1 and due_date was missing."
    )
