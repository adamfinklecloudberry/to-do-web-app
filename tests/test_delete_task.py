"""Tests delete_task"""

from models.task import Task
from tests.helpers import insert_task, get_task_by_id
from flask import url_for


def test_delete_task(client):
    """
    Tests whether a task can be deleted

    Inserts a task and then deletes it, checking for correct status
    code and that the task is gone
    """
    task_id, name, due_date, complete = 1, "Test task", "2023-01-01", False
    insert_task(name, due_date, complete)
    response = client.get(url_for("delete_task", task_id=task_id))
    assert response.status_code == 302  # redirect
    assert get_task_by_id(1) is None
