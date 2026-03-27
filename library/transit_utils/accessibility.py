"""
Accessibility checking utilities for transit stations and stops.
"""

from typing import List, Dict, Optional

KNOWN_FEATURES = [
    "wheelchair_ramp",
    "elevator",
    "tactile_paving",
    "audio_announcements",
    "low_floor_boarding",
    "accessible_toilet",
]


class AccessibilityChecker:
    """Evaluates and filters stations based on accessibility features."""

    def check_station_accessibility(self, station: Dict) -> Dict:
        """Check which accessibility features a station has.

        Args:
            station: Dict with 'name' and 'accessibilityFeatures' list.

        Returns:
            Dict mapping each known feature to True/False, plus station name.
        """
        features = station.get("accessibilityFeatures", [])
        result = {"station": station.get("name", "Unknown")}
        for feature in KNOWN_FEATURES:
            result[feature] = feature in features
        return result

    def get_accessibility_score(self, station: Dict) -> int:
        """Calculate an accessibility score from 0 to 100 for a station.

        Score is based on the proportion of known features present.

        Args:
            station: Dict with 'accessibilityFeatures' list.

        Returns:
            Integer score 0-100.
        """
        features = station.get("accessibilityFeatures", [])
        if not KNOWN_FEATURES:
            return 0
        count = sum(1 for f in KNOWN_FEATURES if f in features)
        return round((count / len(KNOWN_FEATURES)) * 100)

    def filter_stations_by_features(
        self, stations: List[Dict], features: List[str]
    ) -> List[Dict]:
        """Filter stations that have all requested features.

        Args:
            stations: List of station dicts.
            features: List of required feature names.

        Returns:
            Filtered list of stations.
        """
        if not features:
            return stations

        result = []
        for station in stations:
            station_features = station.get("accessibilityFeatures", [])
            if all(f in station_features for f in features):
                result.append(station)
        return result

    def validate_accessibility_data(self, data: Dict) -> Dict:
        """Validate accessibility data for a station.

        Args:
            data: Dict with 'accessibilityFeatures' list.

        Returns:
            Dict with 'valid' bool, 'errors' list, and 'warnings' list.
        """
        errors = []
        warnings = []

        features = data.get("accessibilityFeatures")
        if features is None:
            errors.append("Missing 'accessibilityFeatures' field")
            return {"valid": False, "errors": errors, "warnings": warnings}

        if not isinstance(features, list):
            errors.append("'accessibilityFeatures' must be a list")
            return {"valid": False, "errors": errors, "warnings": warnings}

        for f in features:
            if f not in KNOWN_FEATURES:
                warnings.append(f"Unknown feature: {f}")

        if len(features) == 0:
            warnings.append("No accessibility features listed")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def get_accessibility_summary(self, stations: List[Dict]) -> Dict:
        """Generate an accessibility summary across multiple stations.

        Args:
            stations: List of station dicts.

        Returns:
            Dict with total stations, average score, feature counts, and
            fully accessible count.
        """
        if not stations:
            return {
                "total_stations": 0,
                "average_score": 0,
                "feature_counts": {},
                "fully_accessible_count": 0,
            }

        scores = []
        feature_counts = {f: 0 for f in KNOWN_FEATURES}
        fully_accessible = 0

        for station in stations:
            score = self.get_accessibility_score(station)
            scores.append(score)
            features = station.get("accessibilityFeatures", [])
            for f in KNOWN_FEATURES:
                if f in features:
                    feature_counts[f] += 1
            if score == 100:
                fully_accessible += 1

        return {
            "total_stations": len(stations),
            "average_score": round(sum(scores) / len(scores), 1),
            "feature_counts": feature_counts,
            "fully_accessible_count": fully_accessible,
        }
