"""Tests for bulk adding tasks"""

from flask import url_for
import json


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
        url_for("bulk_add_tasks"),
        data=json.dumps(tasks),
        content_type="application/json",
    )
    assert response.status_code == 201
    assert response.json["message"] == "Tasks added successfully"
    assert response.json["count"] == 2


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
        url_for("bulk_add_tasks"),
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
        url_for("bulk_add_tasks"),
        data=json.dumps(task_with_missing_name),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["error"] == (
        "Each task must have a name and due_date.  "
        "The name was missing and due_date was 2023-10-02."
    )

    response = client.post(
        url_for("bulk_add_tasks"),
        data=json.dumps(task_with_missing_due_date),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["error"] == (
        "Each task must have a name and due_date.  "
        "The name was Task 1 and due_date was missing."
    )
