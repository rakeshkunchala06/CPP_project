"""
Trip planning algorithms for finding optimal paths through a transit network.

Implements shortest-path (by time) and fewest-transfers strategies
using a modified Dijkstra algorithm.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
import heapq

from transitplan.models import TransitNetwork, Stop, Route, Connection


@dataclass
class TripSegment:
    """One leg of a planned trip on a single route."""

    route: Route
    from_stop: Stop
    to_stop: Stop
    travel_minutes: float
    departure_time: str
    arrival_time: str

    def to_dict(self) -> dict:
        return {
            "route_id": self.route.route_id,
            "route_name": self.route.name,
            "from_stop": self.from_stop.name,
            "to_stop": self.to_stop.name,
            "travel_minutes": self.travel_minutes,
            "departure_time": self.departure_time,
            "arrival_time": self.arrival_time,
        }


@dataclass
class TripResult:
    """Complete trip plan from origin to destination."""

    origin: Stop
    destination: Stop
    segments: List[TripSegment] = field(default_factory=list)
    total_minutes: float = 0.0
    total_transfers: int = 0
    total_fare: float = 0.0
    accessibility_score: float = 0.0

    @property
    def is_valid(self) -> bool:
        return len(self.segments) > 0

    def add_segment(self, segment: TripSegment) -> None:
        self.segments.append(segment)
        self.total_minutes += segment.travel_minutes
        if len(self.segments) > 1:
            self.total_transfers += 1

    def to_dict(self) -> dict:
        return {
            "origin": self.origin.name,
            "destination": self.destination.name,
            "segments": [s.to_dict() for s in self.segments],
            "total_minutes": self.total_minutes,
            "total_transfers": self.total_transfers,
            "total_fare": self.total_fare,
            "accessibility_score": self.accessibility_score,
        }


class TripPlanner:
    """
    Plans trips through a transit network using graph search algorithms.

    Supports two strategies:
    - 'shortest': minimizes total travel time
    - 'fewest_transfers': minimizes number of route changes
    """

    TRANSFER_PENALTY_MINUTES = 5.0

    def __init__(self, network: TransitNetwork) -> None:
        self.network = network

    def plan_trip(
        self,
        origin_id: str,
        destination_id: str,
        strategy: str = "shortest",
    ) -> Optional[TripResult]:
        """
        Plan a trip from origin to destination.

        Args:
            origin_id: Stop ID of the starting point
            destination_id: Stop ID of the destination
            strategy: 'shortest' for minimum time, 'fewest_transfers' for minimum transfers

        Returns:
            TripResult if a path is found, None otherwise
        """
        if origin_id not in self.network.stops or destination_id not in self.network.stops:
            return None

        if origin_id == destination_id:
            origin = self.network.stops[origin_id]
            return TripResult(origin=origin, destination=origin)

        if strategy == "fewest_transfers":
            return self._plan_fewest_transfers(origin_id, destination_id)
        else:
            return self._plan_shortest(origin_id, destination_id)

    def _plan_shortest(self, origin_id: str, destination_id: str) -> Optional[TripResult]:
        """Dijkstra-based shortest time path."""
        dist: Dict[str, float] = {origin_id: 0.0}
        prev: Dict[str, Optional[Tuple[str, Connection]]] = {origin_id: None}
        # Priority queue: (cost, stop_id)
        pq: List[Tuple[float, str]] = [(0.0, origin_id)]
        visited = set()

        while pq:
            cost, current = heapq.heappop(pq)
            if current in visited:
                continue
            visited.add(current)

            if current == destination_id:
                break

            for conn in self.network.get_neighbors(current):
                next_id = conn.to_stop.stop_id
                if next_id in visited:
                    continue
                new_cost = cost + conn.travel_minutes
                if next_id not in dist or new_cost < dist[next_id]:
                    dist[next_id] = new_cost
                    prev[next_id] = (current, conn)
                    heapq.heappush(pq, (new_cost, next_id))

        if destination_id not in prev:
            return None

        return self._reconstruct_trip(origin_id, destination_id, prev)

    def _plan_fewest_transfers(self, origin_id: str, destination_id: str) -> Optional[TripResult]:
        """
        BFS-like search that penalizes transfers heavily,
        effectively minimizing the number of route changes.
        """
        dist: Dict[str, float] = {origin_id: 0.0}
        prev: Dict[str, Optional[Tuple[str, Connection]]] = {origin_id: None}
        route_at: Dict[str, Optional[str]] = {origin_id: None}
        pq: List[Tuple[float, str]] = [(0.0, origin_id)]
        visited = set()

        while pq:
            cost, current = heapq.heappop(pq)
            if current in visited:
                continue
            visited.add(current)

            if current == destination_id:
                break

            for conn in self.network.get_neighbors(current):
                next_id = conn.to_stop.stop_id
                if next_id in visited:
                    continue
                transfer_cost = 0.0
                current_route = route_at.get(current)
                if current_route and current_route != conn.route.route_id:
                    transfer_cost = self.TRANSFER_PENALTY_MINUTES * 10
                new_cost = cost + conn.travel_minutes + transfer_cost
                if next_id not in dist or new_cost < dist[next_id]:
                    dist[next_id] = new_cost
                    prev[next_id] = (current, conn)
                    route_at[next_id] = conn.route.route_id
                    heapq.heappush(pq, (new_cost, next_id))

        if destination_id not in prev:
            return None

        return self._reconstruct_trip(origin_id, destination_id, prev)

    def _reconstruct_trip(
        self,
        origin_id: str,
        destination_id: str,
        prev: Dict[str, Optional[Tuple[str, Connection]]],
    ) -> TripResult:
        """Reconstruct the trip path from predecessor map."""
        origin = self.network.stops[origin_id]
        destination = self.network.stops[destination_id]
        result = TripResult(origin=origin, destination=destination)

        path_conns: List[Connection] = []
        current = destination_id
        while prev.get(current) is not None:
            prev_id, conn = prev[current]
            path_conns.append(conn)
            current = prev_id
        path_conns.reverse()

        for conn in path_conns:
            segment = TripSegment(
                route=conn.route,
                from_stop=conn.from_stop,
                to_stop=conn.to_stop,
                travel_minutes=conn.travel_minutes,
                departure_time=conn.departure_time.isoformat(),
                arrival_time=conn.arrival_time.isoformat(),
            )
            result.add_segment(segment)

        return result

    def find_all_paths(
        self, origin_id: str, destination_id: str, max_paths: int = 3
    ) -> List[TripResult]:
        """Find multiple alternative trip plans."""
        results = []
        for strategy in ["shortest", "fewest_transfers"]:
            trip = self.plan_trip(origin_id, destination_id, strategy)
            if trip and trip.is_valid:
                results.append(trip)
        # Deduplicate by segment routes
        seen = set()
        unique = []
        for r in results:
            key = tuple(s.route.route_id for s in r.segments)
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique[:max_paths]
