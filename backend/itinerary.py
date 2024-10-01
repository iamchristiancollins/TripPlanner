# itinerary.py
from flask import Blueprint, request, jsonify, redirect, url_for, flash
from backend.models import db, User, Trip, ItineraryItem, Chatroom
from backend.auth import token_required
from datetime import datetime
import random
import string

itinerary_bp = Blueprint("itinerary", __name__)


@itinerary_bp.route("/<trip_id>/items", methods=["POST"])
@token_required
def add_itinerary_item(current_user, trip_id):
    activity = request.form.get("activity")
    location = request.form.get("location")
    time = request.form.get("time")
    notes = request.form.get("notes")
    if not activity or not location or not time:
        return jsonify({"error": "Invalid input"}), 400

    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    new_item = ItineraryItem(
        trip_id=trip_id,
        activity=activity,
        location=location,
        time=datetime.fromisoformat(time),
        notes=notes,
    )
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for("itinerary", trip_id=trip_id))


def generate_invite_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


@itinerary_bp.route("/new", methods=["POST"])
@token_required
def create_itinerary(current_user):
    trip_name = request.form.get("trip_name")
    if not trip_name:
        return jsonify({"error": "Invalid input"}), 400

    existing_itinerary = Trip.query.filter_by(trip_name=trip_name).first()
    if existing_itinerary:
        flash("Trip already exists!", "warning")
        return redirect(url_for("trip_detail", trip_id=existing_itinerary.id))

    # Create chatroom
    chatroom = Chatroom()
    db.session.add(chatroom)
    db.session.commit()

    invite_code = generate_invite_code()
    new_trip = Trip(
        trip_name=trip_name,
        chatroom_id=chatroom.id,
        invite_code=invite_code,
    )
    new_trip.users.append(current_user)
    db.session.add(new_trip)
    db.session.commit()

    flash("Trip created successfully!", "success")
    return redirect(url_for("trip_detail", trip_id=new_trip.id))


@itinerary_bp.route("/join/", methods=["POST"])
@token_required
def join_itinerary_by_invite(current_user):
    invite_code = request.form.get("invite_code")
    if not invite_code:
        flash("Invite code is required", "warning")
        return redirect(request.url)

    trip = Trip.query.filter_by(invite_code=invite_code).first()
    if not trip:
        flash("Invalid invite code", "danger")
        return redirect(request.url)

    if current_user not in trip.users:
        trip.users.append(current_user)
        db.session.commit()
        flash("You have been added to the itinerary", "success")
        return redirect(url_for("itinerary", trip_id=trip.id))
    else:
        flash("You are already part of this itinerary", "info")
        return redirect(request.url)
