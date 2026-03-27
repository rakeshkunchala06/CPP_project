"""
Validation utilities for transit data inputs.
"""

import re
from typing import Dict, Tuple

VALID_TRANSIT_TYPES = ["bus", "train", "tram", "metro"]
VALID_ACCESSIBILITY_FEATURES = [
    "wheelchair_ramp",
    "elevator",
    "tactile_paving",
    "audio_announcements",
    "low_floor_boarding",
    "accessible_toilet",
]


class TransitValidator:
    """Validates and sanitizes transit-related input data."""

    def validate_stop(self, data: Dict) -> Tuple[bool, list]:
        """Validate stop/station data.

        Args:
            data: Dict with name, latitude, longitude, address, etc.

        Returns:
            Tuple of (is_valid, list of error messages).
        """
        errors = []

        if not data.get("name") or not str(data["name"]).strip():
            errors.append("Stop name is required")

        lat = data.get("latitude")
        if lat is None:
            errors.append("Latitude is required")
        else:
            try:
                lat = float(lat)
                if lat < -90 or lat > 90:
                    errors.append("Latitude must be between -90 and 90")
            except (ValueError, TypeError):
                errors.append("Latitude must be a valid number")

        lng = data.get("longitude")
        if lng is None:
            errors.append("Longitude is required")
        else:
            try:
                lng = float(lng)
                if lng < -180 or lng > 180:
                    errors.append("Longitude must be between -180 and 180")
            except (ValueError, TypeError):
                errors.append("Longitude must be a valid number")

        features = data.get("accessibilityFeatures", [])
        if isinstance(features, list):
            for f in features:
                if f not in VALID_ACCESSIBILITY_FEATURES:
                    errors.append(f"Invalid accessibility feature: {f}")
        elif features is not None:
            errors.append("accessibilityFeatures must be a list")

        transit_types = data.get("transitTypes", [])
        if isinstance(transit_types, list):
            for t in transit_types:
                if t not in VALID_TRANSIT_TYPES:
                    errors.append(f"Invalid transit type: {t}")
        elif transit_types is not None:
            errors.append("transitTypes must be a list")

        return (len(errors) == 0, errors)

    def validate_route(self, data: Dict) -> Tuple[bool, list]:
        """Validate route data.

        Args:
            data: Dict with name, origin, destination, stops, transitType, etc.

        Returns:
            Tuple of (is_valid, list of error messages).
        """
        errors = []

        if not data.get("name") or not str(data["name"]).strip():
            errors.append("Route name is required")

        if not data.get("origin"):
            errors.append("Origin stop ID is required")

        if not data.get("destination"):
            errors.append("Destination stop ID is required")

        if data.get("origin") and data.get("destination"):
            if data["origin"] == data["destination"]:
                errors.append("Origin and destination must be different")

        transit_type = data.get("transitType")
        if transit_type and transit_type not in VALID_TRANSIT_TYPES:
            errors.append(f"Invalid transit type: {transit_type}")

        rating = data.get("accessibilityRating")
        if rating is not None:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    errors.append("Accessibility rating must be between 1 and 5")
            except (ValueError, TypeError):
                errors.append("Accessibility rating must be a number")

        stops = data.get("stops", [])
        if not isinstance(stops, list):
            errors.append("Stops must be a list")

        return (len(errors) == 0, errors)

    def validate_search(self, data: Dict) -> Tuple[bool, list]:
        """Validate search query data.

        Args:
            data: Dict with origin, destination, accessibilityNeeds.

        Returns:
            Tuple of (is_valid, list of error messages).
        """
        errors = []

        if not data.get("origin"):
            errors.append("Origin is required for search")

        if not data.get("destination"):
            errors.append("Destination is required for search")

        needs = data.get("accessibilityNeeds", [])
        if not isinstance(needs, list):
            errors.append("accessibilityNeeds must be a list")
        else:
            for need in needs:
                if need not in VALID_ACCESSIBILITY_FEATURES:
                    errors.append(f"Invalid accessibility need: {need}")

        return (len(errors) == 0, errors)

    def sanitize_input(self, text: str) -> str:
        """Sanitize a text input by stripping whitespace and removing dangerous characters.

        Args:
            text: Raw input string.

        Returns:
            Sanitized string.
        """
        if not isinstance(text, str):
            return ""
        text = text.strip()
        # Remove potential script injection characters
        text = re.sub(r'[<>{}]', '', text)
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text
