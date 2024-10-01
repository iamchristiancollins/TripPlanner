# chat.py
import logging
from flask import Blueprint, request, jsonify
from backend.models import db, Chatroom, ChatLog, Trip
from backend.auth import token_required
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__)

def serialize_chat_log(log):
    return {
        "id": log.id,
        "user_id": log.user_id,
        "username": log.username,
        "message": log.message,
        "timestamp": log.timestamp.isoformat(),
    }

@chat_bp.route("/<trip_id>/messages", methods=["POST"])
@token_required
def add_message(current_user, trip_id):
    message = request.form.get("message")
    if not message:
        return jsonify({"error": "Invalid input"}), 400

    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    chatroom = trip.chatroom
    if not chatroom:
        chatroom = Chatroom()
        trip.chatroom = chatroom
        db.session.add(chatroom)
        db.session.commit()

    new_log = ChatLog(
        chatroom_id=chatroom.id,
        user_id=current_user.id,
        username=current_user.username,
        message=message,
        timestamp=datetime.utcnow(),
    )
    db.session.add(new_log)
    db.session.commit()

    # Log the message
    logger.info(f"Added message: {message} for chatroom_id: {chatroom.id}")

    return jsonify({"message": "Message added", "username": current_user.username}), 201

@chat_bp.route("/<trip_id>/messages", methods=["GET"])
@token_required
def get_messages(current_user, trip_id):
    trip = Trip.query.get(trip_id)
    if not trip or not trip.chatroom:
        return jsonify({"error": "Chatroom not found"}), 404

    chat_logs = [serialize_chat_log(log) for log in trip.chatroom.chat_logs]

    # Log the retrieved messages
    logger.info(f"Retrieved messages for chatroom_id: {trip.chatroom.id} - {chat_logs}")

    return jsonify(chat_logs), 200
