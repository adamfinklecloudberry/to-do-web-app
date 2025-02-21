"""Helper functions for tests"""

from config import db
from models.task import Task
from models.user import User
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash


def insert_task(name: str, due_date: str, complete: bool = False) -> None:
    """Helper function to insert data for tests"""
    # Create a new Task instance
    new_task = Task(name=name, due_date=due_date, complete=complete)

    # Add the new task to the session and commit
    db.session.add(new_task)
    db.session.commit()


def get_task_by_id(task_id: int) -> Task:
    """Return a task from the database by its id"""
    return db.session.get(Task, 1)


def add_test_user():
    """Creates a test user"""
    test_user = User(email="test@user.com", password=generate_password_hash("password"))
    db.session.add(test_user)
    db.session.commit()


def login_test_user(client):
    """Logs the test user in and returns a response"""
    return client.post(
        url_for("login"), data={"email": "test@user.com", "password": "password"}
    )
