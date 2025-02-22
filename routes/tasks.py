"""Routes for CRUD on tasks"""

from flask import Flask, Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required
from config import db
from models.task import Task


tasks_bp = Blueprint("tasks", __name__)


@login_required
@tasks_bp.route("/add", methods=["POST"])
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
            db.session.commit()
            flash("Task added successfully", "success")
        except Exception as e:
            flash("Error in adding task", "error")
            print(f"Error when running add_task: {str(e)}")
    return redirect(url_for("home.home"))


@login_required
@tasks_bp.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id: int):
    task = db.session.get(Task, task_id)

    if task is None:
        flash("Task not found", "error")
        return redirect(url_for("home.home"))

    if request.method == "POST":
        new_name = request.form.get("task")
        task.name = new_name
        db.session.commit()
        return redirect(url_for("home.home"))

    return render_template("edit.html", task_id=task_id, task=task)


@login_required
@tasks_bp.route("/complete/<int:task_id>", methods=["POST"])
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
        task = db.session.get(Task, task_id)

        if task is None:
            flash("Task not found", "error")
            return redirect(url_for("home.home"))

        task.complete = not task.complete
        db.session.commit()  # Commit the changes to the database
        flash("Task completion status updated", "success")
    except Exception as e:
        flash("Error completing task", "error")
        print(f"Error when running complete_task: {str(e)}")

    return redirect(url_for("home.home"))


@login_required
@tasks_bp.route("/delete/<int:task_id>")
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
        task = db.session.get(Task, task_id)

        if task is None:
            flash("Task not found", "error")
            return redirect(url_for("home.home"))

        db.session.delete(task)
        db.session.commit()
        flash("Task deleted successfully", "danger")
    except Exception as e:
        db.session.rollback()  # Rollback the session in case of error
        flash("Error deleting task", "error")
        print(f"Error when running delete_task: {str(e)}")

    return redirect(url_for("home.home"))


@login_required
@tasks_bp.route("/delete_all", methods=["POST"])
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
        db.session.query(Task).delete()
        db.session.commit()
        flash("All tasks deleted successfully", "danger")
    except Exception as e:
        db.session.rollback()  # Rollback the session in case of error
        flash("Error deleting all tasks", "error")
        print(f"Error when running delete_all_tasks: {str(e)}")

    return redirect(url_for("home.home"))
