# app.py
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
    flash,
)
from werkzeug.security import generate_password_hash
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime
import jwt
from backend.itinerary import generate_invite_code

load_dotenv()

app = Flask(__name__)
CORS(app)

# Update the configuration for SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # To suppress a warning

print(
    f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}"
)  # Debugging print statement
print(
    f"os.getenv('DATABASE_URL'): {os.getenv('DATABASE_URL')}"
)  # Debugging print statement

from backend.models import db, User, Trip, Chatroom, ItineraryItem, Budget, Profile

db.init_app(app)

from backend.auth import auth_bp, token_required
from backend.chat import chat_bp
from backend.itinerary import itinerary_bp
from backend.budget import budget_bp
from jwt.exceptions import ExpiredSignatureError

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(chat_bp, url_prefix="/chat")
app.register_blueprint(itinerary_bp, url_prefix="/itinerary")
app.register_blueprint(budget_bp, url_prefix="/budget")


@app.route("/")
def welcome():
    print("Welcome route accessed")  # Debugging print statement
    token = request.cookies.get("x-access-token")
    if token:
        try:
            print("User already logged in")
            data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
            username = data["username"]
            print(f"Token username: {username}")  # Debugging print statement
            return redirect(url_for("mainpage", username=username))
        except ExpiredSignatureError:
            print("Token has expired")  # Debugging print statement
            return redirect(
                url_for("auth.login")
            )  # Redirect to login page or handle accordingly

    return render_template(
        "welcome.html", google_maps_api_key=os.getenv("GOOGLEMAPS_API_KEY")
    )


@app.route("/admit")
def admit():
    return render_template(
        "admit.html", google_maps_api_key=os.getenv("GOOGLEMAPS_API_KEY")
    )


@app.route("/signup")
def signup():
    return render_template(
        "signup.html", google_maps_api_key=os.getenv("GOOGLEMAPS_API_KEY")
    )


@app.route("/main")
def main():
    print("Main route accessed")  # Debugging print statement
    return render_template(
        "mainpage.html", google_maps_api_key=os.getenv("GOOGLEMAPS_API_KEY")
    )


@app.route("/trip")
def trip(username, trip_name):
    return render_template(
        "trip.html", google_maps_api_key=os.getenv("GOOGLEMAPS_API_KEY")
    )


@app.route("/trip/<trip_id>/chat")
@token_required
def trip_chat(current_user, trip_id):
    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404
    return render_template(
        "trip_chat.html",
        trip=trip,
        user=current_user,
        google_maps_api_key=os.getenv("GOOGLEMAPS_API_KEY"),
    )


@app.route("/trip/<trip_id>/budget")
@token_required
def budget_view(current_user, trip_id):
    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    user_budgets = []
    for budget in trip.budgets:
        user = User.query.get(budget.user_id)
        if user:
            user_budget = {"username": user.username, "budget": budget}
            user_budgets.append(user_budget)

    return render_template(
        "budget.html",
        trip=trip,
        user_budgets=user_budgets,
        user=current_user,
        google_maps_api_key=os.getenv("GOOGLEMAPS_API_KEY"),
    )


@app.route("/trip/<trip_id>/itinerary")
@token_required
def itinerary_view(current_user, trip_id):
    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404
    return render_template(
        "itinerary.html",
        trip=trip,
        user=current_user,
        google_maps_api_key=os.getenv("GOOGLEMAPS_API_KEY"),
    )


@app.route("/mainpage/<username>")
@token_required
def mainpage(current_user, username):
    print(f"Mainpage route accessed for user: {username}")  # Debugging print statement
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    past_trips = user.profile.past_trips if user.profile else []
    for trip in past_trips:
        user_names = [u.username for u in trip.users]
        trip.user_names = user_names

    return render_template(
        "mainpage.html",
        user=user,
        trip=past_trips,
        google_maps_api_key=os.getenv("GOOGLEMAPS_API_KEY"),
    )


@app.route("/trip/<trip_id>")
@token_required
def trip_detail(current_user, trip_id):
    print(
        f"Trip detail route accessed for trip_id: {trip_id}"
    )  # Debugging print statement
    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    users = [user.username for user in trip.users]
    trip.user_names = users

    return render_template(
        "trip.html",
        trip=trip,
        user=current_user,
        rapidapi_key=os.getenv("RAPIDAPI_KEY"),
        google_maps_api_key=os.getenv("GOOGLEMAPS_API_KEY"),
    )


def initialize_database():
    with app.app_context():
        db.create_all()  # Create tables based on models

        test_users = [
            {
                "username": "testuser1",
                "password": "testpassword1",
                "email": "testuser1@example.com",
            },
            {
                "username": "testuser2",
                "password": "testpassword2",
                "email": "testuser2@example.com",
            },
        ]

        user_ids = []
        for user_data in test_users:
            user = User.query.filter_by(username=user_data["username"]).first()
            if not user:
                hashed_password = generate_password_hash(user_data["password"])
                user = User(
                    username=user_data["username"],
                    password=hashed_password,
                    email=user_data["email"],
                )
                profile = Profile(name=f"Test User {user_data['username'][-1]}")
                user.profile = profile
                db.session.add(user)
                db.session.commit()
                user_ids.append(user.id)
                print(f"Test user {user.username} created with user_id: {user.id}")
            else:
                user_ids.append(user.id)

        # Check if the itinerary already exists
        existing_trip = Trip.query.filter_by(trip_name="Test Trip").first()
        if not existing_trip:
            # Create a dummy chatroom
            chatroom = Chatroom()
            db.session.add(chatroom)
            db.session.commit()

            # Create a dummy trip
            invite_code = generate_invite_code()
            trip = Trip(
                trip_name="Test Trip",
                chatroom=chatroom,
                invite_code=invite_code,
            )
            trip.users = User.query.filter(User.id.in_(user_ids)).all()
            db.session.add(trip)
            db.session.commit()

            # Add itinerary items
            itinerary_items = [
                ItineraryItem(
                    trip_id=trip.id,
                    activity="Visit Eiffel Tower",
                    location="Paris",
                    time=datetime(2022, 7, 15, 10, 0),
                    notes="Buy tickets online",
                ),
                ItineraryItem(
                    trip_id=trip.id,
                    activity="Lunch at Le Jules Verne",
                    location="Paris",
                    time=datetime(2022, 7, 15, 13, 0),
                    notes="Reservation at 1 PM",
                ),
            ]
            db.session.add_all(itinerary_items)
            db.session.commit()

            # Add budgets
            budgets = [
                Budget(
                    trip_id=trip.id,
                    user_id=user_ids[0],
                    flight=300,
                    hotel=400,
                    food=200,
                    transport=150,
                    activities=200,
                    spending=100,
                ),
                Budget(
                    trip_id=trip.id,
                    user_id=user_ids[1],
                    flight=200,
                    hotel=300,
                    food=100,
                    transport=50,
                    activities=100,
                    spending=80,
                ),
            ]
            db.session.add_all(budgets)
            db.session.commit()

            # Add chat logs
            chat_logs = [
                ChatLog(
                    chatroom_id=chatroom.id,
                    user_id=user_ids[0],
                    username="testuser1",
                    message="Looking forward to the trip!",
                    timestamp=datetime.utcnow(),
                ),
                ChatLog(
                    chatroom_id=chatroom.id,
                    user_id=user_ids[1],
                    username="testuser2",
                    message="Don't forget to pack comfortable shoes.",
                    timestamp=datetime.utcnow(),
                ),
            ]
            db.session.add_all(chat_logs)
            db.session.commit()

            print(f"Dummy trip added with trip_id: {trip.id}")
        else:
            print("Dummy trip already exists")


initialize_database()

if __name__ == "__main__":
    app.run(debug=True)
