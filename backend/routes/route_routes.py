"""CRUD API endpoints for transit routes."""

from flask import Blueprint, request, jsonify
from backend.models import db, RouteModel

route_bp = Blueprint("routes", __name__, url_prefix="/api/routes")


@route_bp.route("", methods=["GET"])
def get_routes():
    """List all routes."""
    routes = RouteModel.query.all()
    return jsonify([r.to_dict() for r in routes]), 200


@route_bp.route("/<int:id>", methods=["GET"])
def get_route(id):
    """Get a single route by ID."""
    route = RouteModel.query.get_or_404(id)
    return jsonify(route.to_dict()), 200


@route_bp.route("", methods=["POST"])
def create_route():
    """Create a new route."""
    data = request.get_json()
    if not data or not data.get("route_id") or not data.get("name"):
        return jsonify({"error": "route_id and name are required"}), 400
    if RouteModel.query.filter_by(route_id=data["route_id"]).first():
        return jsonify({"error": "Route with this route_id already exists"}), 409
    route = RouteModel(
        route_id=data["route_id"],
        name=data["name"],
        route_type=data.get("route_type", "bus"),
        color=data.get("color", "#0000FF"),
        is_accessible=data.get("is_accessible", True),
        fare_zone_start=data.get("fare_zone_start", 1),
        fare_zone_end=data.get("fare_zone_end", 1),
    )
    db.session.add(route)
    db.session.commit()
    return jsonify(route.to_dict()), 201


@route_bp.route("/<int:id>", methods=["PUT"])
def update_route(id):
    """Update an existing route."""
    route = RouteModel.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    route.name = data.get("name", route.name)
    route.route_type = data.get("route_type", route.route_type)
    route.color = data.get("color", route.color)
    route.is_accessible = data.get("is_accessible", route.is_accessible)
    route.fare_zone_start = data.get("fare_zone_start", route.fare_zone_start)
    route.fare_zone_end = data.get("fare_zone_end", route.fare_zone_end)
    db.session.commit()
    return jsonify(route.to_dict()), 200


@route_bp.route("/<int:id>", methods=["DELETE"])
def delete_route(id):
    """Delete a route."""
    route = RouteModel.query.get_or_404(id)
    db.session.delete(route)
    db.session.commit()
    return jsonify({"message": "Route deleted"}), 200
