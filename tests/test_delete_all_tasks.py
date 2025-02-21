"""Tests delete_all_tasks"""

from config import db
from flask_app import Task
from tests.helper import insert_task


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
    assert db.session.get(Task, 1) is None
    assert db.session.get(Task, 2) is None
