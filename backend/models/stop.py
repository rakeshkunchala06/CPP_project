"""Stop database model."""

from backend.models import db


class StopModel(db.Model):
    """Represents a transit stop in the database."""

    __tablename__ = "stops"

    id = db.Column(db.Integer, primary_key=True)
    stop_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    wheelchair_accessible = db.Column(db.Boolean, default=True)
    has_audio_announcements = db.Column(db.Boolean, default=False)
    has_visual_displays = db.Column(db.Boolean, default=False)
    has_tactile_paving = db.Column(db.Boolean, default=False)
    zone = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            "id": self.id,
            "stop_id": self.stop_id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "wheelchair_accessible": self.wheelchair_accessible,
            "has_audio_announcements": self.has_audio_announcements,
            "has_visual_displays": self.has_visual_displays,
            "has_tactile_paving": self.has_tactile_paving,
            "zone": self.zone,
        }
