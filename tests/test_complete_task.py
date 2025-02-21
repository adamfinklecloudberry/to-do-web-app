from config import db
from flask_app import Task
from helper import insert_task


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

    task = db.session.get(Task, 1)
    task_id = 1
    complete = 1
    assert task.name == "Test task"
    assert task.due_date == "2023-01-01"
    assert task.complete == True