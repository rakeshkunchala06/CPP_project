"""
Amazon Location Service Wrapper.

Provides maps and geocoding functionality.
Uses mock coordinates in local mode.
"""


class LocationService:
    """Wrapper for Amazon Location Service (maps and geocoding)."""

    MOCK_LOCATIONS = {
        "Connolly Station": {"lat": 53.3509, "lng": -6.2500},
        "Tara Street": {"lat": 53.3475, "lng": -6.2545},
        "Pearse Station": {"lat": 53.3435, "lng": -6.2480},
        "Grand Canal Dock": {"lat": 53.3395, "lng": -6.2390},
        "Lansdowne Road": {"lat": 53.3340, "lng": -6.2280},
        "Heuston Station": {"lat": 53.3464, "lng": -6.2923},
        "O'Connell Street": {"lat": 53.3498, "lng": -6.2603},
        "St Stephen's Green": {"lat": 53.3382, "lng": -6.2591},
    }

    def __init__(self, use_mock=True):
        self.use_mock = use_mock

    def geocode(self, address):
        """Convert an address to coordinates."""
        if self.use_mock:
            for name, coords in self.MOCK_LOCATIONS.items():
                if name.lower() in address.lower():
                    return {
                        "address": address,
                        "latitude": coords["lat"],
                        "longitude": coords["lng"],
                        "mode": "mock",
                    }
            # Default Dublin city center
            return {
                "address": address,
                "latitude": 53.3498,
                "longitude": -6.2603,
                "mode": "mock",
            }
        return None

    def reverse_geocode(self, latitude, longitude):
        """Convert coordinates to an address."""
        if self.use_mock:
            closest = None
            min_dist = float("inf")
            for name, coords in self.MOCK_LOCATIONS.items():
                dist = abs(coords["lat"] - latitude) + abs(coords["lng"] - longitude)
                if dist < min_dist:
                    min_dist = dist
                    closest = name
            return {
                "latitude": latitude,
                "longitude": longitude,
                "address": closest or "Unknown Location",
                "mode": "mock",
            }
        return None

    def calculate_distance(self, lat1, lng1, lat2, lng2):
        """Calculate distance between two points in km."""
        import math
        r = 6371
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlng / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        return round(r * c, 2)

    def health_check(self):
        return {
            "service": "Amazon Location Service",
            "status": "healthy",
            "mode": "local_mock" if self.use_mock else "production",
            "mock_locations_count": len(self.MOCK_LOCATIONS),
        }
