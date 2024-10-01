# budget.py
from flask import Blueprint, request, jsonify, redirect, url_for
from backend.models import db, Budget, Trip
from backend.auth import token_required
from datetime import datetime

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/<trip_id>/expenses", methods=["POST"])
@token_required
def add_expense(current_user, trip_id):
    data = request.get_json()
    category = data.get("category")
    amount = data.get("amount")
    description = data.get("description")
    if not category or not amount or not description:
        return jsonify({"error": "Invalid input"}), 400

    budget = Budget.query.filter_by(trip_id=trip_id, user_id=current_user.id).first()
    if not budget:
        budget = Budget(trip_id=trip_id, user_id=current_user.id)
        db.session.add(budget)

    # Here you might need to handle expenses per category; adjust your Budget model accordingly
    setattr(budget, category, amount)
    db.session.commit()
    return jsonify({"message": "Expense added"}), 201


@budget_bp.route("/<trip_id>/expenses", methods=["GET"])
@token_required
def get_expenses(current_user, trip_id):
    budget = Budget.query.filter_by(trip_id=trip_id, user_id=current_user.id).first()
    if not budget:
        return jsonify({"error": "No budget found"}), 404
    budget_data = {
        "flight": budget.flight,
        "hotel": budget.hotel,
        "food": budget.food,
        "transport": budget.transport,
        "activities": budget.activities,
        "spending": budget.spending,
    }
    return jsonify(budget_data), 200


@budget_bp.route("/<trip_id>/updated", methods=["POST"])
@token_required
def update_expenses(current_user, trip_id):
    budget_items = []
    for field in ["flight", "hotel", "food", "transport", "activities", "spending"]:
        value = request.form.get(field)
        try:
            budget_items.append(float(value))
        except (ValueError, TypeError):
            budget_items.append(0)

    budget = Budget.query.filter_by(trip_id=trip_id, user_id=current_user.id).first()
    if not budget:
        budget = Budget(trip_id=trip_id, user_id=current_user.id)
        db.session.add(budget)

    budget.flight = budget_items[0]
    budget.hotel = budget_items[1]
    budget.food = budget_items[2]
    budget.transport = budget_items[3]
    budget.activities = budget_items[4]
    budget.spending = budget_items[5]
    db.session.commit()

    return redirect(url_for("budget", trip_id=trip_id))
