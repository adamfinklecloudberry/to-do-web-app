"""
A To-Do app

Allows users to manage a list of tasks

Users can add, complete, delete, and view tasks.

Stores tasks in a SQLite database and provides both a web interface and
a JSON API for task management
"""

import os
import secrets
import sqlite3
from flask import Flask, render_template, request, redirect, flash, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Configure the SQLAlchemy Database
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(os.path.dirname(__file__), "database.db")}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the SQLAlchemy object
# Configuration based on the environment
if os.environ.get("FLASK_ENV") == "production":
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///production.db"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///test.db"  # or an in-memory database
    )
db = SQLAlchemy(app)


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Text, nullable=False)
    complete = db.Column(db.Boolean, default=False, nullable=False)


def init_db():
    """
    Initializes the database

    Creates the SQLAlchemy database and the tasks table if it does not
    already exist

    Args:
        db_path (str): The path to the SQLite database file.
    """
    with app.app_context():
        db.create_all()


if not os.path.exists(app.config["SQLALCHEMY_DATABASE_URI"]):
    init_db()


@app.route("/")
def home() -> str:
    """
    Renders the home page

    Retrieves all tasks from the database and renders the home HTML
    template with the list of tasks

    Excludes complete tasks if the request includes an argument
    telling it to

    Returns:
        str: The rendered HTML template for the home page."""
    try:
        tasks = Task.query.all()  # Get all tasks
    except Exception as e:
        print(f"Error querying tasks from table {Task.__tablename__}: {e}")
        return f"Database error: {e}", 500

    show_incomplete = request.args.get("incomplete", "false").lower() == "true"
    filtered_tasks = (
        [task for task in tasks if not task.complete] if show_incomplete else tasks
    )

    return render_template("index.html", tasks=filtered_tasks)


@app.route("/add", methods=["POST"])
def add_task():
    """
    Adds a task to the task list

    Retrieves the task name and due date from the request form,
    adds the task to the database, and redirects to the home page

    Flashes a success message if the operation is successful;
    else, flashes an error message

    Returns:
        Response: A redirect response to the home page.
    """
    name = request.form.get("task")
    due_date = request.form.get("due_date")
    if name and due_date:
        try:
            task = Task(name=name, due_date=due_date, complete=False)
            db.session.add(task)

            # with sqlite3.connect(app.config["DATABASE"]) as conn:
            #     cursor = conn.cursor()
            #     cursor.execute(
            #         "INSERT INTO tasks (name, due_date) VALUES (?, ?)",
            #         (task, due_date),
            #     )
            db.session.commit()
            flash("Task added successfully", "success")
        except Exception as e:
            flash("Error in adding task", "error")
            print(f"Error when running add_task: {str(e)}")
    return redirect("/")


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id: int):
    task = Task.query.get(task_id)

    if task is None:
        flash("Task not found", "error")
        return redirect("/")

    if request.method == "POST":
        new_name = request.form.get("task")
        task.name = new_name
        db.session.commit()
        return redirect("/")

    return render_template("edit.html", task_id=task_id, task=task)


@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id: int):
    """
    Marks a task as completed

    Toggles the completion status of a task identified by its ID,
    updates the task in the database, and redirects to the home page

    Flashes a success message if the operation is successful;
    else, flashes an error message

    Args:
        task_id (int): The ID of the task to be marked as completed.

    Returns:
        Response: A redirect response to the home page.
    """
    try:
        # Retrieve the task using SQLAlchemy
        task = Task.query.get(task_id)

        if task is None:
            flash("Task not found", "error")
            return redirect("/")

        # Toggle the completion status
        task.complete = not task.complete
        db.session.commit()  # Commit the changes to the database
        flash("Task completion status updated", "success")
    except Exception as e:
        flash("Error completing task", "error")
        print(f"Error when running complete_task: {str(e)}")

    return redirect("/")


@app.route("/delete/<int:task_id>")
def delete_task(task_id: int):
    """
    Deletes a task from the list

    Removes a task identified by its ID from the database and redirects
    to the home page

    Flashes a success message if the operation is successful;
    else, flashes an error message

    Args:
        task_id (int): The ID of the task to be deleted.

    Returns:
        Response: A redirect response to the home page.
    """
    try:
        # Retrieve the task using SQLAlchemy
        task = Task.query.get(task_id)

        if task is None:
            flash("Task not found", "error")
            return redirect("/")

        # Delete the task
        db.session.delete(task)
        db.session.commit()  # Commit the changes to the database
        flash("Task deleted successfully", "danger")
    except Exception as e:
        db.session.rollback()  # Rollback the session in case of error
        flash("Error deleting task", "error")
        print(f"Error when running delete_task: {str(e)}")

    return redirect("/")


@app.route("/delete_all", methods=["POST"])
def delete_all_tasks():
    """
    Deletes all tasks from the list

    Executes a DELETE statement to clear the tasks table

    Flashes a success message if the operation is successful;
    else, flashes an error message

    This endpoint is intended to be called via a POST request,
    typically from a form submission or an AJAX request.

    Returns:
        Response: A redirect response to the home page after the
                  deletion operation
    """
    try:
        # Delete all tasks using SQLAlchemy
        db.session.query(Task).delete()  # This will delete all tasks
        db.session.commit()  # Commit the changes to the database
        flash("All tasks deleted successfully", "danger")
    except Exception as e:
        db.session.rollback()  # Rollback the session in case of error
        flash("Error deleting all tasks", "error")
        print(f"Error when running delete_all_tasks: {str(e)}")

    return redirect("/")


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """
    Returns a json containing all the tasks

    Queries the database for all tasks and returns them as a JSON
    response

    If the query is successful, returns a list of tasks; if an
    error occurs during the database operation, prints the error
    message to the console

    Returns:
        Response: A JSON response containing a list of all tasks in the
                  database. If an error occurs, it returns a 500
                  status code with an error message.
    """
    try:
        # Retrieve all tasks using SQLAlchemy
        tasks = Task.query.all()  # This will return a list of Task objects

        # Convert the list of Task objects to a list of dictionaries
        tasks_list = [
            {
                "id": task.id,
                "name": task.name,
                "due_date": task.due_date,
                "complete": task.complete,
            }
            for task in tasks
        ]

        return jsonify(tasks_list)  # Return the list of tasks as JSON
    except Exception as e:
        error_message = f"Error when returning all tasks: {str(e)}"
        print(error_message)
        return jsonify({"error": error_message}), 500  # Return a 500 error status


@app.route("/bulk_add", methods=["POST"])
def bulk_add_tasks():
    """
    Bulk inserts tasks into the task list from a JSON payload

    Accepts a JSON payload containing a list of tasks and inserts them
    into the database

    Each task should have a 'name' and 'due_date' field. If the input
    data is not in the expected format, it returns a 400 error with a
    descriptive message.

    Args:
        None: This function reads the JSON payload from the request
              body.

    Returns:
        Response: A JSON response indicating the success of the
                  operation, including the count of tasks added. If the
                  input data is invalid, it returns a 400 status code
                  with an error message. If an error occurs during the
                  database operation, it returns a 500 status code with
                  an error message.
    """
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return (
                jsonify({"error": "Invalid data format.  Expected a list of tasks."}),
                400,
            )

        tasks_to_insert = []
        for task in data:
            name = task.get("name")
            due_date = task.get("due_date")
            complete = task.get("complete", False)

            if name and due_date:
                # Create a new Task instance
                new_task = Task(name=name, due_date=due_date, complete=complete)
                tasks_to_insert.append(new_task)
            else:
                return (
                    jsonify(
                        {
                            "error": (
                                "Each task must have a name and due_date.  "
                                f"The name was {name if name else 'missing'} "
                                f"and due_date was {due_date if due_date else 'missing'}."
                            )
                        }
                    ),
                    400,
                )

        # Step to add all tasks to the session and commit
        db.session.add_all(tasks_to_insert)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Tasks added successfully",
                    "count": len(tasks_to_insert),
                }
            ),
            201,
        )

    except Exception as e:
        print(f"Error when running bulk_add_tasks: {str(e)}")
        db.session.rollback()  # Rollback the session in case of error
        return (
            jsonify({"error": "An error occurred while adding tasks."}),
            500,
        )


if __name__ == "__main__":
    app.run(debug=True)
