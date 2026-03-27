"""CRUD API endpoints for trips."""

from flask import Blueprint, request, jsonify
from backend.models import db, TripModel

trip_bp = Blueprint("trips", __name__, url_prefix="/api/trips")


@trip_bp.route("", methods=["GET"])
def get_trips():
    """List all trips."""
    trips = TripModel.query.all()
    return jsonify([t.to_dict() for t in trips]), 200


@trip_bp.route("/<int:id>", methods=["GET"])
def get_trip(id):
    """Get a single trip by ID."""
    trip = TripModel.query.get_or_404(id)
    return jsonify(trip.to_dict()), 200


@trip_bp.route("", methods=["POST"])
def create_trip():
    """Create a new trip."""
    data = request.get_json()
    if not data or not data.get("trip_id"):
        return jsonify({"error": "trip_id is required"}), 400
    if TripModel.query.filter_by(trip_id=data["trip_id"]).first():
        return jsonify({"error": "Trip with this trip_id already exists"}), 409
    trip = TripModel(
        trip_id=data["trip_id"],
        origin_stop_id=data.get("origin_stop_id", ""),
        destination_stop_id=data.get("destination_stop_id", ""),
        departure_time=data.get("departure_time"),
        strategy=data.get("strategy", "shortest"),
        total_minutes=data.get("total_minutes", 0.0),
        total_transfers=data.get("total_transfers", 0),
        total_fare=data.get("total_fare", 0.0),
        accessibility_score=data.get("accessibility_score", 0.0),
        status=data.get("status", "planned"),
    )
    db.session.add(trip)
    db.session.commit()
    return jsonify(trip.to_dict()), 201


@trip_bp.route("/<int:id>", methods=["PUT"])
def update_trip(id):
    """Update an existing trip."""
    trip = TripModel.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    trip.origin_stop_id = data.get("origin_stop_id", trip.origin_stop_id)
    trip.destination_stop_id = data.get("destination_stop_id", trip.destination_stop_id)
    trip.departure_time = data.get("departure_time", trip.departure_time)
    trip.strategy = data.get("strategy", trip.strategy)
    trip.total_minutes = data.get("total_minutes", trip.total_minutes)
    trip.total_transfers = data.get("total_transfers", trip.total_transfers)
    trip.total_fare = data.get("total_fare", trip.total_fare)
    trip.accessibility_score = data.get("accessibility_score", trip.accessibility_score)
    trip.status = data.get("status", trip.status)
    db.session.commit()
    return jsonify(trip.to_dict()), 200


@trip_bp.route("/<int:id>", methods=["DELETE"])
def delete_trip(id):
    """Delete a trip."""
    trip = TripModel.query.get_or_404(id)
    db.session.delete(trip)
    db.session.commit()
    return jsonify({"message": "Trip deleted"}), 200
