"""Tests get_tasks"""

from tests.helpers import insert_task
from flask import url_for


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
    response = client.get(url_for("get_tasks"))
    assert response.status_code == 200
    assert response.json == [
        {"id": 1, "name": name, "due_date": due_date, "complete": complete},
        {"id": 2, "name": name, "due_date": due_date, "complete": complete},
    ]
