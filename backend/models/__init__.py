"""SQLAlchemy database models for the transit planner."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


from backend.models.route import RouteModel
from backend.models.stop import StopModel
from backend.models.schedule import ScheduleModel
from backend.models.trip import TripModel
from backend.models.accessibility_feature import AccessibilityFeatureModel

__all__ = [
    "db",
    "RouteModel",
    "StopModel",
    "ScheduleModel",
    "TripModel",
    "AccessibilityFeatureModel",
]
