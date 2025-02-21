"""A helper function for tests"""

from config import db
from models.task import Task


def insert_task(name: str, due_date: str, complete: bool) -> None:
    """Helper function to insert data for tests"""
    # Create a new Task instance
    new_task = Task(name=name, due_date=due_date, complete=complete)

    # Add the new task to the session and commit
    db.session.add(new_task)
    db.session.commit()
