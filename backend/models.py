# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Association table for many-to-many relationship between users and trips
user_trips = db.Table(
    "user_trips",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("trip_id", db.Integer, db.ForeignKey("trips.id"), primary_key=True),
)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile = db.relationship("Profile", uselist=False, backref="user")
    # Add trips relationship
    trips = db.relationship("Trip", secondary=user_trips, back_populates="users")
    budgets = db.relationship("Budget", backref="user", lazy=True)
    chat_logs = db.relationship("ChatLog", backref="user", lazy=True)


class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # Remove the past_trips relationship
    # You can access trips via user.trips


class Trip(db.Model):
    __tablename__ = "trips"
    id = db.Column(db.Integer, primary_key=True)
    trip_name = db.Column(db.String(100), nullable=False)
    invite_code = db.Column(db.String(10), unique=True)
    # Correct the users relationship
    users = db.relationship("User", secondary=user_trips, back_populates="trips")
    itinerary_items = db.relationship("ItineraryItem", backref="trip", lazy=True)
    budgets = db.relationship("Budget", backref="trip", lazy=True)
    chatroom_id = db.Column(db.Integer, db.ForeignKey("chatrooms.id"))
    chatroom = db.relationship("Chatroom", backref="trip", uselist=False)


class ItineraryItem(db.Model):
    __tablename__ = "itinerary_items"
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    activity = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.String(200))


class Budget(db.Model):
    __tablename__ = "budgets"
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    flight = db.Column(db.Float, default=0)
    hotel = db.Column(db.Float, default=0)
    food = db.Column(db.Float, default=0)
    transport = db.Column(db.Float, default=0)
    activities = db.Column(db.Float, default=0)
    spending = db.Column(db.Float, default=0)


class Chatroom(db.Model):
    __tablename__ = "chatrooms"
    id = db.Column(db.Integer, primary_key=True)
    chat_logs = db.relationship("ChatLog", backref="chatroom", lazy=True)


class ChatLog(db.Model):
    __tablename__ = "chat_logs"
    id = db.Column(db.Integer, primary_key=True)
    chatroom_id = db.Column(db.Integer, db.ForeignKey("chatrooms.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    username = db.Column(db.String(80))
    message = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
