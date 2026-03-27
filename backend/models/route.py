"""Route database model."""

from backend.models import db


class RouteModel(db.Model):
    """Represents a transit route in the database."""

    __tablename__ = "routes"

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    route_type = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), default="#0000FF")
    is_accessible = db.Column(db.Boolean, default=True)
    fare_zone_start = db.Column(db.Integer, default=1)
    fare_zone_end = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            "id": self.id,
            "route_id": self.route_id,
            "name": self.name,
            "route_type": self.route_type,
            "color": self.color,
            "is_accessible": self.is_accessible,
            "fare_zone_start": self.fare_zone_start,
            "fare_zone_end": self.fare_zone_end,
        }
