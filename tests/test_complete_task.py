from flask import url_for
from config import db
from models.task import Task
from tests.helpers import insert_task, get_task_by_id


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
    response = client.post(url_for("tasks.complete_task", task_id=1))
    assert response.status_code == 302  # redirect

    task = get_task_by_id(1)
    task_id = 1
    complete = 1
    assert task.name == "Test task"
    assert task.due_date == "2023-01-01"
    assert task.complete == True
