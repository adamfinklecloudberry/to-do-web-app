from flask import url_for
from config import db
from flask_app import app
from models.task import Task


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
    response = client.get(url_for("edit", task_id=1))
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
    updated_task = db.session.get(Task, 1)  # Fetch the task with id = 1
    assert updated_task.name == "Updated Task"
