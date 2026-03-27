"""CRUD API endpoints for transit schedules."""

from flask import Blueprint, request, jsonify
from backend.models import db, ScheduleModel

schedule_bp = Blueprint("schedules", __name__, url_prefix="/api/schedules")


@schedule_bp.route("", methods=["GET"])
def get_schedules():
    """List all schedules."""
    schedules = ScheduleModel.query.all()
    return jsonify([s.to_dict() for s in schedules]), 200


@schedule_bp.route("/<int:id>", methods=["GET"])
def get_schedule(id):
    """Get a single schedule by ID."""
    schedule = ScheduleModel.query.get_or_404(id)
    return jsonify(schedule.to_dict()), 200


@schedule_bp.route("", methods=["POST"])
def create_schedule():
    """Create a new schedule."""
    data = request.get_json()
    if not data or not data.get("schedule_id"):
        return jsonify({"error": "schedule_id is required"}), 400
    if ScheduleModel.query.filter_by(schedule_id=data["schedule_id"]).first():
        return jsonify({"error": "Schedule with this schedule_id already exists"}), 409
    schedule = ScheduleModel(
        schedule_id=data["schedule_id"],
        route_id=data.get("route_id", ""),
        stop_id=data.get("stop_id", ""),
        departure_time=data.get("departure_time", "08:00"),
        arrival_time=data.get("arrival_time", "08:10"),
        day_of_week=data.get("day_of_week", "weekday"),
        is_active=data.get("is_active", True),
    )
    db.session.add(schedule)
    db.session.commit()
    return jsonify(schedule.to_dict()), 201


@schedule_bp.route("/<int:id>", methods=["PUT"])
def update_schedule(id):
    """Update an existing schedule."""
    schedule = ScheduleModel.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    schedule.route_id = data.get("route_id", schedule.route_id)
    schedule.stop_id = data.get("stop_id", schedule.stop_id)
    schedule.departure_time = data.get("departure_time", schedule.departure_time)
    schedule.arrival_time = data.get("arrival_time", schedule.arrival_time)
    schedule.day_of_week = data.get("day_of_week", schedule.day_of_week)
    schedule.is_active = data.get("is_active", schedule.is_active)
    db.session.commit()
    return jsonify(schedule.to_dict()), 200


@schedule_bp.route("/<int:id>", methods=["DELETE"])
def delete_schedule(id):
    """Delete a schedule."""
    schedule = ScheduleModel.query.get_or_404(id)
    db.session.delete(schedule)
    db.session.commit()
    return jsonify({"message": "Schedule deleted"}), 200
