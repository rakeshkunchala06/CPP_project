"""Schedule database model."""

from backend.models import db


class ScheduleModel(db.Model):
    """Represents a transit schedule entry in the database."""

    __tablename__ = "schedules"

    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.String(50), unique=True, nullable=False)
    route_id = db.Column(db.String(50), nullable=False)
    stop_id = db.Column(db.String(50), nullable=False)
    departure_time = db.Column(db.String(10), nullable=False)
    arrival_time = db.Column(db.String(10), nullable=False)
    day_of_week = db.Column(db.String(20), default="weekday")
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "schedule_id": self.schedule_id,
            "route_id": self.route_id,
            "stop_id": self.stop_id,
            "departure_time": self.departure_time,
            "arrival_time": self.arrival_time,
            "day_of_week": self.day_of_week,
            "is_active": self.is_active,
        }
