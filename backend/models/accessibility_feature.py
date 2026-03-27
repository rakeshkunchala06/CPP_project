"""AccessibilityFeature database model."""

from backend.models import db


class AccessibilityFeatureModel(db.Model):
    """Represents an accessibility feature record in the database."""

    __tablename__ = "accessibility_features"

    id = db.Column(db.Integer, primary_key=True)
    feature_id = db.Column(db.String(50), unique=True, nullable=False)
    stop_id = db.Column(db.String(50), nullable=False)
    feature_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    condition_rating = db.Column(db.Float, default=1.0)

    def to_dict(self):
        return {
            "id": self.id,
            "feature_id": self.feature_id,
            "stop_id": self.stop_id,
            "feature_type": self.feature_type,
            "description": self.description,
            "is_available": self.is_available,
            "condition_rating": self.condition_rating,
        }
