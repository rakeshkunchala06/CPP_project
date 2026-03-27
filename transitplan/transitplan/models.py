"""
Core data models for transit planning.

Provides OOP representations of stops, routes, schedules,
connections, and the overall transit network graph.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import time, timedelta


@dataclass
class Stop:
    """Represents a transit stop or station."""

    stop_id: str
    name: str
    latitude: float
    longitude: float
    wheelchair_accessible: bool = True
    has_audio_announcements: bool = False
    has_visual_displays: bool = False
    has_tactile_paving: bool = False
    zone: int = 1

    def distance_to(self, other: "Stop") -> float:
        """Calculate approximate distance in km using Haversine-like estimation."""
        import math
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return 6371 * c  # Earth radius in km

    def to_dict(self) -> dict:
        return {
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


@dataclass
class Schedule:
    """Represents a scheduled departure from a stop on a route."""

    schedule_id: str
    route_id: str
    stop_id: str
    departure_time: time
    arrival_time: time
    day_of_week: str = "weekday"  # weekday, saturday, sunday
    is_active: bool = True

    def duration_minutes(self) -> float:
        """Calculate duration between arrival and departure in minutes."""
        dep = timedelta(hours=self.departure_time.hour, minutes=self.departure_time.minute)
        arr = timedelta(hours=self.arrival_time.hour, minutes=self.arrival_time.minute)
        diff = arr - dep
        if diff.total_seconds() < 0:
            diff += timedelta(days=1)
        return diff.total_seconds() / 60

    def to_dict(self) -> dict:
        return {
            "schedule_id": self.schedule_id,
            "route_id": self.route_id,
            "stop_id": self.stop_id,
            "departure_time": self.departure_time.isoformat(),
            "arrival_time": self.arrival_time.isoformat(),
            "day_of_week": self.day_of_week,
            "is_active": self.is_active,
        }


@dataclass
class Route:
    """Represents a transit route with an ordered list of stops."""

    route_id: str
    name: str
    route_type: str  # bus, rail, tram, ferry
    stops: List[Stop] = field(default_factory=list)
    schedules: List[Schedule] = field(default_factory=list)
    color: str = "#0000FF"
    is_accessible: bool = True
    fare_zone_start: int = 1
    fare_zone_end: int = 1

    def add_stop(self, stop: Stop) -> None:
        """Add a stop to this route."""
        self.stops.append(stop)

    def remove_stop(self, stop_id: str) -> bool:
        """Remove a stop by ID. Returns True if found and removed."""
        for i, s in enumerate(self.stops):
            if s.stop_id == stop_id:
                self.stops.pop(i)
                return True
        return False

    def get_stop_ids(self) -> List[str]:
        """Return list of stop IDs in order."""
        return [s.stop_id for s in self.stops]

    def total_distance(self) -> float:
        """Calculate total route distance in km."""
        total = 0.0
        for i in range(len(self.stops) - 1):
            total += self.stops[i].distance_to(self.stops[i + 1])
        return total

    def to_dict(self) -> dict:
        return {
            "route_id": self.route_id,
            "name": self.name,
            "route_type": self.route_type,
            "stops": [s.to_dict() for s in self.stops],
            "color": self.color,
            "is_accessible": self.is_accessible,
            "fare_zone_start": self.fare_zone_start,
            "fare_zone_end": self.fare_zone_end,
        }


@dataclass
class Connection:
    """Represents a connection between two stops on a route."""

    from_stop: Stop
    to_stop: Stop
    route: Route
    departure_time: time
    arrival_time: time
    travel_minutes: float

    def to_dict(self) -> dict:
        return {
            "from_stop": self.from_stop.stop_id,
            "to_stop": self.to_stop.stop_id,
            "route_id": self.route.route_id,
            "departure_time": self.departure_time.isoformat(),
            "arrival_time": self.arrival_time.isoformat(),
            "travel_minutes": self.travel_minutes,
        }


class TransitNetwork:
    """
    Graph-based transit network supporting route lookups,
    neighbor discovery, and transfer point detection.
    """

    def __init__(self) -> None:
        self.stops: Dict[str, Stop] = {}
        self.routes: Dict[str, Route] = {}
        self.connections: List[Connection] = []
        self._adjacency: Dict[str, List[Connection]] = {}

    def add_stop(self, stop: Stop) -> None:
        """Register a stop in the network."""
        self.stops[stop.stop_id] = stop

    def add_route(self, route: Route) -> None:
        """Register a route and its stops."""
        self.routes[route.route_id] = route
        for stop in route.stops:
            if stop.stop_id not in self.stops:
                self.add_stop(stop)

    def add_connection(self, connection: Connection) -> None:
        """Add a directed connection between two stops."""
        self.connections.append(connection)
        from_id = connection.from_stop.stop_id
        if from_id not in self._adjacency:
            self._adjacency[from_id] = []
        self._adjacency[from_id].append(connection)

    def get_neighbors(self, stop_id: str) -> List[Connection]:
        """Get all outgoing connections from a stop."""
        return self._adjacency.get(stop_id, [])

    def find_transfer_points(self) -> List[Stop]:
        """
        Find stops served by multiple routes (transfer points).
        A transfer point is a stop that appears on 2+ routes.
        """
        stop_route_count: Dict[str, Set[str]] = {}
        for route in self.routes.values():
            for stop in route.stops:
                if stop.stop_id not in stop_route_count:
                    stop_route_count[stop.stop_id] = set()
                stop_route_count[stop.stop_id].add(route.route_id)

        transfer_stops = []
        for stop_id, route_ids in stop_route_count.items():
            if len(route_ids) >= 2:
                transfer_stops.append(self.stops[stop_id])
        return transfer_stops

    def get_routes_for_stop(self, stop_id: str) -> List[Route]:
        """Get all routes serving a given stop."""
        result = []
        for route in self.routes.values():
            if stop_id in route.get_stop_ids():
                result.append(route)
        return result

    def build_connections_from_routes(self, default_travel_minutes: float = 5.0) -> None:
        """
        Automatically build connections from route stop sequences.
        Each consecutive pair of stops on a route gets a connection.
        """
        base_hour = 6
        for route in self.routes.values():
            for i in range(len(route.stops) - 1):
                dep = time(hour=base_hour, minute=(i * int(default_travel_minutes)) % 60)
                arr_min = (i + 1) * int(default_travel_minutes)
                arr = time(hour=base_hour + arr_min // 60, minute=arr_min % 60)
                conn = Connection(
                    from_stop=route.stops[i],
                    to_stop=route.stops[i + 1],
                    route=route,
                    departure_time=dep,
                    arrival_time=arr,
                    travel_minutes=default_travel_minutes,
                )
                self.add_connection(conn)

    def to_dict(self) -> dict:
        return {
            "stops": {sid: s.to_dict() for sid, s in self.stops.items()},
            "routes": {rid: r.to_dict() for rid, r in self.routes.items()},
            "connections": [c.to_dict() for c in self.connections],
            "transfer_points": [s.stop_id for s in self.find_transfer_points()],
        }
