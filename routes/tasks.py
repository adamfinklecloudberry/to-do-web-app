"""Routes for CRUD on tasks"""

from flask import (
    Flask,
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    url_for,
    send_file,
    abort,
)
from flask_login import login_required
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os
import io
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
    """
    Edit the name of a task.

    This route handles both GET and POST requests to edit the name of a task.
    On a GET request, it renders a template where the user can input a new name for the task.
    On a POST request, it updates the task name in the database and redirects to the home page.

    Parameters:
    task_id (int): The ID of the task to be edited.

    Returns:
    flask.Response: The rendered template for GET requests or a redirect response for POST requests.

    Raises:
    None

    Example:
    GET /edit/1
    POST /edit/1 with form data {'task': 'New Task Name'}
    """
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

        # Check if the task has an associated file
        if task.file_name:
            s3_key = f"task_{task_id}/{task.file_name}"
            try:
                # Delete the file from S3
                s3_client.delete_object(
                    Bucket=os.getenv("S3_BUCKET", "default-bucket-name"), Key=s3_key
                )
            except NoCredentialsError:
                flash("Credentials not available", "error")
                return redirect(url_for("home.home"))
            except ClientError as e:
                flash(f"Error deleting file from S3: {str(e)}", "error")
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
    Deletes all tasks from the list and their associated files from S3.

    This function performs the following steps sequentially for each task:
    1. Deletes the associated file from S3 if it exists.
    2. Deletes the task from the database.
    3. Commits the changes to the database.

    If any error occurs during the deletion process, the database session is rolled back,
    and an error message is flashed to the user. The function then returns a redirect
    response to the home page.

    Args:
        None

    Returns:
        Response: A redirect response to the home page after the deletion operation.

    Raises:
        NoCredentialsError: If AWS credentials are not available.
        ClientError: If there is an error deleting the file from S3.
        Exception: If any other error occurs during the deletion process.

    Flash Messages:
        - "All tasks and associated files deleted successfully" (success message)
        - "Credentials not available" (error message)
        - "Error deleting file from S3: {error_message}" (error message)
        - "Error deleting all tasks" (error message)

    Example:
        POST /delete_all
        - Deletes all tasks and their associated files from S3.
        - Redirects to the home page with a success or error message.

    Notes:
        - The function ensures that each task is deleted from the database immediately
          after its associated file is deleted from S3.
        - If any exception occurs, the database session is rolled back to maintain data integrity.
    """
    try:
        # Query all tasks
        tasks = db.session.query(Task).all()

        for task in tasks:
            # Delete the associated file from S3 if it exists
            if task.file_name:
                s3_key = f"task_{task.id}/{task.file_name}"
                try:
                    # Delete the file from S3
                    s3_client.delete_object(Bucket=os.getenv("S3_BUCKET"), Key=s3_key)
                except NoCredentialsError:
                    flash("Credentials not available", "error")
                    db.session.rollback()  # Rollback the session in case of error
                    return redirect(url_for("home.home"))
                except ClientError as e:
                    flash(f"Error deleting file from S3: {str(e)}", "error")
                    db.session.rollback()  # Rollback the session in case of error
                    return redirect(url_for("home.home"))

            # Delete the task from the database
            db.session.delete(task)
            db.session.commit()
        flash("All tasks deleted successfully", "danger")
    except Exception as e:
        db.session.rollback()  # Rollback the session in case of error
        flash("Error deleting all tasks", "error")
        print(f"Error when running delete_all_tasks: {str(e)}")

    return redirect(url_for("home.home"))


@login_required
@tasks_bp.route("/upload/<int:task_id>", methods=["POST"])
def upload_file(task_id: int):
    """
    Upload a file to an S3 bucket associated with a specific task.

    This route handles POST requests to upload a file to an S3 bucket. The file is
    associated with a specific task identified by `task_id`. The file is stored in
    the S3 bucket with a key that includes the task ID and the original filename.
    The task object in the database is updated with the filename of the uploaded file.

    Parameters:
    task_id (int): The ID of the task to which the file will be associated.

    Returns:
    str: A message indicating the result of the file upload operation.
          - 'No file part' if no file is present in the request.
          - 'No selected file' if no file is selected for upload.
          - 'File successfully uploaded to S3 for task {task_id}' if the file is successfully uploaded.
          - 'Task not found' with a 404 status code if the task does not exist.
          - 'Credentials not available' if AWS credentials are not available.
          - 'Error uploading file: {error_message}' if an error occurs during the upload process.

    Raises:
    Exception: Any exception that occurs during the file upload process.

    Environment Variables:
    S3_REGION (str): The AWS region where the S3 bucket is located.
    S3_BUCKET (str): The name of the S3 bucket where the file will be uploaded.

    Example:
    To upload a file to the S3 bucket for task with ID 123, send a POST request to
    `/upload/123` with a file attached in the request.

    Note:
    - The user must be logged in to access this route.
    - The route uses the `boto3` library to interact with AWS S3.
    - The task object is updated in the database with the filename of the uploaded file.
    - Proper error handling is in place to manage different failure scenarios.
    """
    if "file" not in request.files:
        flash("No file part", "error")
        return redirect(url_for("home.home"))

    file = request.files["file"]
    if file.filename == "":
        flash("No selected file", "error")
        return redirect(url_for("home.home"))

    if file:
        try:
            # Initialize the S3 client
            s3_client = boto3.client("s3", region_name=os.getenv("S3_REGION"))

            # You can use task_id to create a unique path in S3 if needed
            s3_key = f"task_{task_id}/{file.filename}"

            # Check if a file already exists in S3
            try:
                s3_client.head_object(Bucket=os.getenv("S3_BUCKET"), Key=s3_key)
                # If the file exists, delete it
                s3_client.delete_object(Bucket=os.getenv("S3_BUCKET"), Key=s3_key)
                flash("File overwritten", "danger")
            except ClientError as e:
                if e.response['Error']['Code'] == "404":
                    # The file does not exist, so we can proceed with the upload
                    pass
                else:
                    raise e

            # Upload the new file to S3
            s3_client.upload_fileobj(file, os.getenv("S3_BUCKET"), s3_key)

            # Update the Task object with the file name
            task = Task.query.get(task_id)
            if task:
                task.file_name = file.filename
                db.session.commit()
                flash("File uploaded successfully", "success")
            else:
                flash("Task not found", "error")
                return redirect(url_for("home.home"))
        except NoCredentialsError:
            flash("Credentials not available", "error")
            return redirect(url_for("home.home"))
        except Exception as e:
            flash(f"Error uploading file: {str(e)}", "error")
            return redirect(url_for("home.home"))

    return redirect(url_for("home.home"))


@login_required
@tasks_bp.route("/download/<int:task_id>")
def download_file(task_id: int):
    """
    Download a file from an S3 bucket associated with a specific task.

    This route handles GET requests to download a file from an S3 bucket. The file is
    associated with a specific task identified by `task_id`. The file is retrieved from
    the S3 bucket using the task ID and the filename stored in the task object. The file
    is then sent to the client for download.

    Parameters:
    task_id (int): The ID of the task from which the file will be downloaded.

    Returns:
    Flask Response: A response containing the file for download.
          - The file is sent as an attachment with the original filename.
          - The MIME type is set to 'application/octet-stream' to indicate a binary file.
    str: An error message if an error occurs during the file download process.
          - 'Error downloading file: {error_message}' with a 500 status code if a client error occurs.

    Raises:
    HTTPException: A 404 error if the task or file is not found.

    Environment Variables:
    S3_BUCKET (str): The name of the S3 bucket where the file is stored.

    Example:
    To download a file associated with a task with ID 123, send a GET request to
    `/download/123`.

    Note:
    - The user must be logged in to access this route.
    - The route uses the `boto3` library to interact with AWS S3.
    - The task object is queried from the database to retrieve the filename.
    - Proper error handling is in place to manage different failure scenarios.
    """
    task = Task.query.get(task_id)
    if not task or not task.file_name:
        abort(404, description="Task or file not found")

    s3_key = f"task_{task_id}/{task.file_name}"
    try:
        # Initialize the S3 client
        s3_client = boto3.client("s3", region_name=os.getenv("S3_REGION"))

        # Download the file from S3
        response = s3_client.get_object(Bucket=os.getenv("S3_BUCKET"), Key=s3_key)
        file_content = response["Body"].read()

        # Send the file to the client for download
        return send_file(
            io.BytesIO(file_content),
            as_attachment=True,
            download_name=task.file_name,
            mimetype="application/octet-stream",
        )
    except ClientError as e:
        return f"Error downloading file: {str(e)}", 500
