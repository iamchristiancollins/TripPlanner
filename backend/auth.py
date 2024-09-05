from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import mongo
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
            current_user = mongo.db.users.find_one({"username": data["username"]})
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

        if mongo.db.users.find_one({"username": username}):
            flash("User already exists", "warning")
            return render_template("signup.html")

        if not checkPassword(password):
            flash("Did not meet password requirements", "warning")
            return render_template("signup.html")

        hashed_password = generate_password_hash(password)
        user_id = mongo.db.users.insert_one(
            {
                "username": username,
                "password": hashed_password,
                "email": email,
                "profile": {"name": "", "past_trips": []},
            }
        ).inserted_id

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
    countLow, countUp = 0,0
    for i in pw:
        cond1 = i.islower()
        cond2 = i.isupper()
        if(cond1 == 1):
            countLow +=1
        if(cond2 == 1):
            countUp +=1
    if(countLow==0):
        return False
    if(countUp==0):
        return False
    cond3 = pw[-1].isnumeric()
    if(cond3 != 1):
        return False
    if len(pw) < 8:
        return False
    else:
        return True

@auth_bp.route("/admit", methods=["GET", "POST"])

def login():
    # data = request.get_json()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = mongo.db.users.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            token = jwt.encode(
                {
                    "username": user["username"],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
                },
                os.getenv("SECRET_KEY"),
                algorithm="HS256",
            )
            response = redirect(url_for("mainpage", username=username))
            response.set_cookie("x-access-token", token)
            return response
            return jsonify({"token": token}), 200
        flash("Incorrect username or password", "warning")
        return render_template("admit.html")
        # return render_template('login.html', error="Incorrect username or password")
    return render_template("login.html")
    # return jsonify({"error": "Invalid username or password"}), 401


@auth_bp.route("/logout")
def logout():
    response = redirect(url_for("welcome"))
    response.set_cookie("x-access-token", "", expires=0)
    return response
