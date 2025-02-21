from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import select
from config import db
from models.task import Task


home_bp = Blueprint('home', __name__)


@home_bp.route("/")
@login_required
def home() -> str:
    """
    Renders the home page

    Retrieves all tasks from the database and renders the home HTML
    template with the list of tasks

    Excludes complete tasks if the request includes an argument
    telling it to

    Returns:
        str: The rendered HTML template for the home page.
    """
    try:
        tasks = db.session.scalars(select(Task)).all()
    except Exception as e:
        print(f"Error querying tasks from table {Task.__tablename__}: {e}")
        return f"Database error: {e}", 500

    show_incomplete = request.args.get("incomplete", "false").lower() == "true"
    filtered_tasks = (
        [task for task in tasks if not task.complete] if show_incomplete else tasks
    )

    return render_template(
        "index.html", tasks=filtered_tasks, number_of_tasks=len(filtered_tasks)
    )
