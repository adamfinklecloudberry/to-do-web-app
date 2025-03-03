from flask_sqlalchemy import SQLAlchemy

# Import the db instance from the main app
from config import db


class Task(db.Model):
    __tablename__ = "task"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Text, nullable=False)
    complete = db.Column(db.Boolean, default=False, nullable=False)
    file_name = db.Column(db.Text, nullable=True)
