"""
Route optimization utilities for accessible transit trip planning.
"""

import math
from typing import List, Dict, Optional


class RouteOptimizer:
    """Finds, filters, and optimizes transit routes based on accessibility needs."""

    EARTH_RADIUS_KM = 6371.0

    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points using the haversine formula.

        Args:
            lat1: Latitude of point 1 in degrees.
            lng1: Longitude of point 1 in degrees.
            lat2: Latitude of point 2 in degrees.
            lng2: Longitude of point 2 in degrees.

        Returns:
            Distance in kilometres.
        """
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return self.EARTH_RADIUS_KM * c

    def find_routes(self, origin: Dict, destination: Dict, stops: List[Dict]) -> List[Dict]:
        """Find possible routes between origin and destination through available stops.

        Args:
            origin: Dict with 'name', 'latitude', 'longitude'.
            destination: Dict with 'name', 'latitude', 'longitude'.
            stops: List of stop dicts with at least 'name', 'latitude', 'longitude'.

        Returns:
            List of route dicts sorted by total distance.
        """
        if not origin or not destination:
            return []

        routes = []

        # Direct route
        direct_dist = self.calculate_distance(
            origin["latitude"], origin["longitude"],
            destination["latitude"], destination["longitude"],
        )
        routes.append({
            "name": f"{origin['name']} -> {destination['name']}",
            "origin": origin["name"],
            "destination": destination["name"],
            "stops": [],
            "total_distance_km": round(direct_dist, 2),
            "num_transfers": 0,
        })

        # Routes through each intermediate stop
        for stop in stops:
            dist_to_stop = self.calculate_distance(
                origin["latitude"], origin["longitude"],
                stop["latitude"], stop["longitude"],
            )
            dist_from_stop = self.calculate_distance(
                stop["latitude"], stop["longitude"],
                destination["latitude"], destination["longitude"],
            )
            total = dist_to_stop + dist_from_stop
            routes.append({
                "name": f"{origin['name']} -> {stop['name']} -> {destination['name']}",
                "origin": origin["name"],
                "destination": destination["name"],
                "stops": [stop],
                "total_distance_km": round(total, 2),
                "num_transfers": 1,
            })

        routes.sort(key=lambda r: r["total_distance_km"])
        return routes

    def calculate_travel_time(self, route: Dict, avg_speed_kmh: float = 30.0) -> Dict:
        """Estimate travel time for a route.

        Args:
            route: Route dict containing 'total_distance_km' and 'num_transfers'.
            avg_speed_kmh: Average speed in km/h (default 30).

        Returns:
            Dict with travel_minutes, transfer_minutes, and total_minutes.
        """
        distance = route.get("total_distance_km", 0)
        transfers = route.get("num_transfers", 0)
        travel_min = (distance / avg_speed_kmh) * 60 if avg_speed_kmh > 0 else 0
        transfer_min = transfers * 5  # 5 min per transfer
        total = travel_min + transfer_min
        return {
            "travel_minutes": round(travel_min, 1),
            "transfer_minutes": transfer_min,
            "total_minutes": round(total, 1),
        }

    def filter_accessible_routes(self, routes: List[Dict], requirements: List[str]) -> List[Dict]:
        """Filter routes that meet all accessibility requirements.

        Args:
            routes: List of route dicts, each with 'stops' containing accessibility info.
            requirements: List of required accessibility features.

        Returns:
            Filtered list of routes where every stop meets requirements.
        """
        if not requirements:
            return routes

        filtered = []
        for route in routes:
            stops = route.get("stops", [])
            if not stops:
                # Direct route with no intermediate stops passes by default
                filtered.append(route)
                continue
            all_accessible = True
            for stop in stops:
                features = stop.get("accessibilityFeatures", [])
                if not all(req in features for req in requirements):
                    all_accessible = False
                    break
            if all_accessible:
                filtered.append(route)
        return filtered

    def optimize_route(self, route: Dict, preference: str = "fastest") -> Dict:
        """Add optimization metadata to a route based on preference.

        Args:
            route: Route dict.
            preference: One of 'fastest', 'accessible', 'least_transfers'.

        Returns:
            Route dict with added 'optimization' metadata.
        """
        result = dict(route)
        time_info = self.calculate_travel_time(route)

        if preference == "fastest":
            result["optimization"] = {
                "preference": "fastest",
                "estimated_minutes": time_info["total_minutes"],
                "score": max(0, 100 - time_info["total_minutes"]),
            }
        elif preference == "accessible":
            stops = route.get("stops", [])
            total_features = 0
            for stop in stops:
                total_features += len(stop.get("accessibilityFeatures", []))
            avg_features = total_features / len(stops) if stops else 6
            result["optimization"] = {
                "preference": "accessible",
                "avg_accessibility_features": round(avg_features, 1),
                "score": min(100, round(avg_features * 16.67)),
            }
        elif preference == "least_transfers":
            transfers = route.get("num_transfers", 0)
            result["optimization"] = {
                "preference": "least_transfers",
                "transfers": transfers,
                "score": max(0, 100 - transfers * 25),
            }
        else:
            result["optimization"] = {
                "preference": preference,
                "score": 0,
                "error": "Unknown preference",
            }

        return result
