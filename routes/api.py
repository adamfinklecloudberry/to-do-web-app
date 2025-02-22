from config import db
from models.task import Task
from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy import select


api_bp = Blueprint("api", __name__)


@login_required
@api_bp.route("/api/tasks", methods=["GET"])
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
        tasks = db.session.scalars(select(Task))

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
        # Return the list of tasks as JSON
        return jsonify(tasks_list)
    except Exception as e:
        error_message = f"Error when returning all tasks: {str(e)}"
        print(error_message)
        # Return a 500 error status
        return jsonify({"error": error_message}), 500


@login_required
@api_bp.route("/api/bulk_add", methods=["POST"])
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
