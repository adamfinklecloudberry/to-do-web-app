"""Tests delete_task"""

from config import db
from flask_app import Task
from tests.helper import insert_task


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
    assert db.session.get(Task, 1) is None
