"""CRUD API endpoints for transit stops."""

from flask import Blueprint, request, jsonify
from backend.models import db, StopModel

stop_bp = Blueprint("stops", __name__, url_prefix="/api/stops")


@stop_bp.route("", methods=["GET"])
def get_stops():
    """List all stops."""
    stops = StopModel.query.all()
    return jsonify([s.to_dict() for s in stops]), 200


@stop_bp.route("/<int:id>", methods=["GET"])
def get_stop(id):
    """Get a single stop by ID."""
    stop = StopModel.query.get_or_404(id)
    return jsonify(stop.to_dict()), 200


@stop_bp.route("", methods=["POST"])
def create_stop():
    """Create a new stop."""
    data = request.get_json()
    if not data or not data.get("stop_id") or not data.get("name"):
        return jsonify({"error": "stop_id and name are required"}), 400
    if StopModel.query.filter_by(stop_id=data["stop_id"]).first():
        return jsonify({"error": "Stop with this stop_id already exists"}), 409
    stop = StopModel(
        stop_id=data["stop_id"],
        name=data["name"],
        latitude=data.get("latitude", 0.0),
        longitude=data.get("longitude", 0.0),
        wheelchair_accessible=data.get("wheelchair_accessible", True),
        has_audio_announcements=data.get("has_audio_announcements", False),
        has_visual_displays=data.get("has_visual_displays", False),
        has_tactile_paving=data.get("has_tactile_paving", False),
        zone=data.get("zone", 1),
    )
    db.session.add(stop)
    db.session.commit()
    return jsonify(stop.to_dict()), 201


@stop_bp.route("/<int:id>", methods=["PUT"])
def update_stop(id):
    """Update an existing stop."""
    stop = StopModel.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    stop.name = data.get("name", stop.name)
    stop.latitude = data.get("latitude", stop.latitude)
    stop.longitude = data.get("longitude", stop.longitude)
    stop.wheelchair_accessible = data.get("wheelchair_accessible", stop.wheelchair_accessible)
    stop.has_audio_announcements = data.get("has_audio_announcements", stop.has_audio_announcements)
    stop.has_visual_displays = data.get("has_visual_displays", stop.has_visual_displays)
    stop.has_tactile_paving = data.get("has_tactile_paving", stop.has_tactile_paving)
    stop.zone = data.get("zone", stop.zone)
    db.session.commit()
    return jsonify(stop.to_dict()), 200


@stop_bp.route("/<int:id>", methods=["DELETE"])
def delete_stop(id):
    """Delete a stop."""
    stop = StopModel.query.get_or_404(id)
    db.session.delete(stop)
    db.session.commit()
    return jsonify({"message": "Stop deleted"}), 200
