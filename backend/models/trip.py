"""Trip database model."""

from backend.models import db


class TripModel(db.Model):
    """Represents a planned trip in the database."""

    __tablename__ = "trips"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.String(50), unique=True, nullable=False)
    origin_stop_id = db.Column(db.String(50), nullable=False)
    destination_stop_id = db.Column(db.String(50), nullable=False)
    departure_time = db.Column(db.String(10), nullable=True)
    strategy = db.Column(db.String(30), default="shortest")
    total_minutes = db.Column(db.Float, default=0.0)
    total_transfers = db.Column(db.Integer, default=0)
    total_fare = db.Column(db.Float, default=0.0)
    accessibility_score = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default="planned")

    def to_dict(self):
        return {
            "id": self.id,
            "trip_id": self.trip_id,
            "origin_stop_id": self.origin_stop_id,
            "destination_stop_id": self.destination_stop_id,
            "departure_time": self.departure_time,
            "strategy": self.strategy,
            "total_minutes": self.total_minutes,
            "total_transfers": self.total_transfers,
            "total_fare": self.total_fare,
            "accessibility_score": self.accessibility_score,
            "status": self.status,
        }
