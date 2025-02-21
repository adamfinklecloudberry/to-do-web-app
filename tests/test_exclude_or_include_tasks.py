"""
Tests for including and excluding data from the task list
"""

from flask_app import app
from models.task import Task
from models.user import User
from tests.helpers import add_test_user, login_test_user, insert_task
from flask import url_for


def test_home_exclude_complete_tasks(client):
    """
    Tests the home route to verify that it correctly excludes complete
    tasks when the 'incomplete' query parameter is set to 'true'

    Sets up the database with a mix of complete and incomplete tasks,
    sends a GET request to the home route with the 'incomplete'
    parameter, and asserts that only incomplete tasks are present in
    the response data
    """
    # Add a test user
    add_test_user()

    # Add test data to the database with SQLAlchemy
    insert_task("Task 1", "2023-10-01")
    insert_task("Task 2", "2023-10-02", True)
    insert_task("Task 3", "2023-10-03")

    # Log in the test user
    response = login_test_user(client)

    # Check if login was successful
    assert response.status_code == 302  # Assuming a redirect after login

    # Test: Request the home route with the 'incomplete' parameter set to 'true'
    response = client.get(url_for("home", incomplete=True))

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
    # Add a test user
    add_test_user()

    # Add test data to the database
    insert_task("Task 1", "2023-10-01")
    insert_task("Task 2", "2023-10-02", True)
    insert_task("Task 3", "2023-10-03")

    # Log in the test user
    response = login_test_user(client)

    # Check if login was successful
    assert response.status_code == 302  # Assuming a redirect after login

    # Test: Request the home route without the 'incomplete' parameter
    response = client.get(url_for("home"))

    # Assert: Check that the response status code is 200 (OK)
    assert response.status_code == 200

    # Assert: Check that the response contains all tasks
    assert b"Task 1" in response.data
    # This task is complete and should be included
    assert b"Task 2" in response.data
    assert b"Task 3" in response.data
