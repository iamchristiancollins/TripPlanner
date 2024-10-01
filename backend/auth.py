# auth.py
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import db, User
import jwt
import datetime
from functools import wraps
import os

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/admit", methods=["GET"])
def templ():
    return render_template("admit.html")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("x-access-token")
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        try:
            data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
            current_user = User.query.filter_by(username=data["username"]).first()
        except Exception as e:
            return jsonify({"error": "Token is invalid"}), 401
        return f(current_user, *args, **kwargs)

    return decorated


@auth_bp.route("/signup", methods=["GET", "POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    if request.method == "POST":
        if not username or not password or not email:
            flash("Invalid Input", "warning")
            return render_template("signup.html")

        if User.query.filter_by(username=username).first():
            flash("User already exists", "warning")
            return render_template("signup.html")

        if not checkPassword(password):
            flash("Did not meet password requirements", "warning")
            return render_template("signup.html")

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()

        # Generate token for the new user
        token = jwt.encode(
            {
                "username": username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            },
            os.getenv("SECRET_KEY"),
            algorithm="HS256",
        )

        # Set the token in the response cookies
        response = redirect(url_for("mainpage", username=username))
        response.set_cookie("x-access-token", token)

        return response

    return render_template("signup.html")


def checkPassword(pw):
    countLow, countUp = 0, 0
    for i in pw:
        cond1 = i.islower()
        cond2 = i.isupper()
        if cond1 == 1:
            countLow += 1
        if cond2 == 1:
            countUp += 1
    if countLow == 0:
        return False
    if countUp == 0:
        return False
    cond3 = pw[-1].isnumeric()
    if cond3 != 1:
        return False
    if len(pw) < 8:
        return False
    else:
        return True


@auth_bp.route("/admit", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            token = jwt.encode(
                {
                    "username": user.username,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
                },
                os.getenv("SECRET_KEY"),
                algorithm="HS256",
            )
            response = redirect(url_for("mainpage", username=username))
            response.set_cookie("x-access-token", token)
            return response
        flash("Incorrect username or password", "warning")
        return render_template("admit.html")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    response = redirect(url_for("welcome"))
    response.set_cookie("x-access-token", "", expires=0)
    return response
