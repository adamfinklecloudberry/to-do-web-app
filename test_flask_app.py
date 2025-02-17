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
from flask import Flask, flash, get_flashed_messages
import sqlite3
from flask_app import app, init_db


@pytest.fixture
def client():
    """
    Creates a test client for the Flask app

    Sets up the Flask application in testing mode and initializes
    a temporary database for the tests using a NamedTemporaryFile,
    which is automatically deleted after the tests are run

    Returns:
        Flask test client: A test client that can be used to simulate
        requests to the application during testing.
    """
    app.config["TESTING"] = True
    with tempfile.NamedTemporaryFile(delete=True) as temp_db:
        app.config["DATABASE"] = temp_db.name
        init_db()
        with app.test_client() as client:
            yield client


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
        with sqlite3.connect(app.config["DATABASE"]) as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE tasks")  # Drop the table to simulate an error

    response = client.post("/add", data={"task": "Test Task", "due_date": "2023-12-31"})
    assert response.status_code == 302  # redirect
    with app.app_context():
        assert "Error in adding task" in [
            m[1] for m in get_flashed_messages(with_categories=True)
        ]


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
    with sqlite3.connect(app.config["DATABASE"]) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (name, due_date, complete) VALUES (?, ?, ?)",
            (name, due_date, complete),
        )
        conn.commit()


def get_task(task_id: int) -> None:
    """
    Helper function for finding tasks for tests

    Returns:
        The task in the database with this id
    """
    with sqlite3.connect(app.config["DATABASE"]) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        )
        return cursor.fetchone()


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

    task_data = get_task(1)
    task_id = 1
    complete = 1
    assert task_data == (task_id, name, due_date, complete)


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
        [1, name, due_date, complete],
        [2, name, due_date, complete],
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
