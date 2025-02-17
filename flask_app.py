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
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    jsonify,
)


app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config["DATABASE"] = os.path.join(os.path.dirname(__file__), "tasks.db")


def init_db():
    """
    Initializes the database

    Creates the SQLite database and the tasks table if it does not
    already exist

    Args:
        db_path (str): The path to the SQLite database file.
    """
    with sqlite3.connect(app.config["DATABASE"], timeout=5) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                due_date TEXT NOT NULL,
                complete BOOLEAN NOT NULL DEFAULT 0
            )
        """
        )
        conn.commit()


if not os.path.exists(app.config["DATABASE"]):
    init_db()


@app.route("/")
def home() -> str:
    """
    Renders the home page

    Retrieves all tasks from the database and renders the home HTML
    template with the list of tasks

    Returns:
        str: The rendered HTML template for the home page."""
    with sqlite3.connect(app.config["DATABASE"]) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
    return render_template("index.html", tasks=tasks)


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
    try:
        task = request.form.get("task")
        due_date = request.form.get("due_date")
        if task and due_date:
            with sqlite3.connect(app.config["DATABASE"]) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO tasks (name, due_date) VALUES (?, ?)",
                    (task, due_date),
                )
                conn.commit()
                flash("Task added successfully", "success")
    except Exception as e:
        flash("Error in adding task", "error")
        print(f"Error when running add_task: {str(e)}")
    return redirect("/")


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
        with sqlite3.connect(app.config["DATABASE"]) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tasks SET complete = NOT complete WHERE id = ?",
                (task_id,),
            )
            conn.commit()
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
        with sqlite3.connect(app.config["DATABASE"]) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            flash("Task deleted successfully", "danger")
    except Exception as e:
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
        with sqlite3.connect(app.config["DATABASE"]) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks")
            conn.commit()
            flash("All tasks deleted successfully", "danger")
    except Exception as e:
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
        with sqlite3.connect(app.config["DATABASE"]) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks")
            tasks = cursor.fetchall()
        return jsonify(tasks)
    except Exception as e:
        error_message = f"Error when returning all tasks: {str(e)}"
        print(error_message)
        return jsonify({"error": error_message})


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
                tasks_to_insert.append((name, due_date, complete))
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

        with sqlite3.connect(app.config["DATABASE"]) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO tasks (name, due_date, complete) VALUES (?, ?, ?)",
                tasks_to_insert,
            )
            conn.commit()

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
        return (
            jsonify({"error": f"An error occurred while adding tasks."}),
            500,
        )


if __name__ == "__main__":
    app.run(debug=True)
