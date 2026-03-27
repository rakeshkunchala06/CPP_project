"""
Accessibility scoring and feature management for transit stops and routes.

Evaluates wheelchair access, audio announcements, visual displays,
and tactile paving to produce a composite accessibility score.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

from transitplan.models import Stop, Route


class AccessibilityType(Enum):
    """Types of accessibility features."""
    WHEELCHAIR = "wheelchair"
    AUDIO = "audio"
    VISUAL = "visual"
    TACTILE = "tactile"


@dataclass
class AccessibilityFeature:
    """Represents a specific accessibility feature at a stop or on a route."""

    feature_id: str
    feature_type: AccessibilityType
    description: str
    is_available: bool = True
    condition_rating: float = 1.0  # 0.0 to 1.0

    def to_dict(self) -> dict:
        return {
            "feature_id": self.feature_id,
            "feature_type": self.feature_type.value,
            "description": self.description,
            "is_available": self.is_available,
            "condition_rating": self.condition_rating,
        }


class AccessibilityScorer:
    """
    Calculates accessibility scores for stops, routes, and trips.

    Scoring weights:
    - Wheelchair access:      40%
    - Audio announcements:    25%
    - Visual displays:        20%
    - Tactile paving:         15%
    """

    WEIGHTS: Dict[str, float] = {
        "wheelchair": 0.40,
        "audio": 0.25,
        "visual": 0.20,
        "tactile": 0.15,
    }

    def __init__(self, custom_weights: Optional[Dict[str, float]] = None) -> None:
        if custom_weights:
            self.weights = custom_weights
        else:
            self.weights = self.WEIGHTS.copy()

    def score_stop(self, stop: Stop) -> float:
        """
        Calculate accessibility score for a single stop (0.0 - 1.0).
        """
        score = 0.0
        if stop.wheelchair_accessible:
            score += self.weights["wheelchair"]
        if stop.has_audio_announcements:
            score += self.weights["audio"]
        if stop.has_visual_displays:
            score += self.weights["visual"]
        if stop.has_tactile_paving:
            score += self.weights["tactile"]
        return round(score, 2)

    def score_route(self, route: Route) -> float:
        """
        Calculate average accessibility score across all stops on a route.
        Returns 0.0 if route has no stops.
        """
        if not route.stops:
            return 0.0
        total = sum(self.score_stop(s) for s in route.stops)
        return round(total / len(route.stops), 2)

    def score_trip(self, stops: List[Stop]) -> float:
        """
        Calculate the minimum accessibility score along a trip path.
        The trip is only as accessible as its least accessible stop.
        """
        if not stops:
            return 0.0
        return min(self.score_stop(s) for s in stops)

    def get_accessibility_report(self, stop: Stop) -> Dict[str, object]:
        """Generate a detailed accessibility report for a stop."""
        return {
            "stop_id": stop.stop_id,
            "stop_name": stop.name,
            "overall_score": self.score_stop(stop),
            "features": {
                "wheelchair_accessible": stop.wheelchair_accessible,
                "audio_announcements": stop.has_audio_announcements,
                "visual_displays": stop.has_visual_displays,
                "tactile_paving": stop.has_tactile_paving,
            },
            "recommendations": self._get_recommendations(stop),
        }

    def _get_recommendations(self, stop: Stop) -> List[str]:
        """Generate improvement recommendations for a stop."""
        recs = []
        if not stop.wheelchair_accessible:
            recs.append("Install wheelchair ramps and accessible platforms")
        if not stop.has_audio_announcements:
            recs.append("Add audio announcement system for visually impaired passengers")
        if not stop.has_visual_displays:
            recs.append("Install visual display boards for hearing impaired passengers")
        if not stop.has_tactile_paving:
            recs.append("Add tactile paving for guidance of visually impaired passengers")
        if not recs:
            recs.append("This stop meets all accessibility criteria")
        return recs

    def filter_accessible_routes(
        self, routes: List[Route], min_score: float = 0.5
    ) -> List[Route]:
        """Filter routes that meet a minimum accessibility score threshold."""
        return [r for r in routes if self.score_route(r) >= min_score]

    def rank_routes_by_accessibility(self, routes: List[Route]) -> List[Route]:
        """Sort routes by accessibility score, highest first."""
        return sorted(routes, key=lambda r: self.score_route(r), reverse=True)
