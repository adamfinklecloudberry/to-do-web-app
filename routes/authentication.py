"""User authentication routes"""

from config import db, login_manager
from models.task import Task
from models.user import User
from flask import request, render_template, Blueprint, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select


authentication_bp = Blueprint("authentication", __name__)


@authentication_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(
            request.form["password"], method="pbkdf2:sha256"
        )
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("authentication.login"))
    return render_template("register.html")


@authentication_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            user.logged_in = True
            db.session.commit()
            return redirect(url_for("authentication.dashboard"))
        else:
            flash("Login failed. Check your email and password.", "danger")
    return render_template("login.html")


@authentication_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@authentication_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("authentication.login"))


@login_manager.user_loader
def load_user(user_id):
    return db.session.scalar(select(User).where(User.id == user_id))
