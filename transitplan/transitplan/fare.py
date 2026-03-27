"""
Fare estimation module for transit trips.

Supports zone-based, flat-rate, and distance-based fare models.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

from transitplan.models import Stop, Route


class FareType(Enum):
    """Fare calculation methods."""
    FLAT = "flat"
    ZONE_BASED = "zone_based"
    DISTANCE_BASED = "distance_based"


@dataclass
class FareRule:
    """Defines a fare rule for a route or network segment."""

    rule_id: str
    fare_type: FareType
    base_fare: float
    per_zone_charge: float = 0.50
    per_km_charge: float = 0.15
    transfer_discount: float = 0.25  # 25% discount on transfers
    concession_discount: float = 0.50  # 50% for concession holders
    max_fare: float = 10.0
    min_fare: float = 1.0

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "fare_type": self.fare_type.value,
            "base_fare": self.base_fare,
            "per_zone_charge": self.per_zone_charge,
            "per_km_charge": self.per_km_charge,
            "transfer_discount": self.transfer_discount,
            "concession_discount": self.concession_discount,
        }


class FareCalculator:
    """
    Calculates fares for trips based on configurable fare rules.
    Supports multiple fare types and discount schemes.
    """

    def __init__(self, default_rule: Optional[FareRule] = None) -> None:
        self.default_rule = default_rule or FareRule(
            rule_id="default",
            fare_type=FareType.ZONE_BASED,
            base_fare=2.00,
        )
        self.route_rules: Dict[str, FareRule] = {}

    def set_route_rule(self, route_id: str, rule: FareRule) -> None:
        """Assign a specific fare rule to a route."""
        self.route_rules[route_id] = rule

    def get_rule_for_route(self, route_id: str) -> FareRule:
        """Get the fare rule applicable to a route."""
        return self.route_rules.get(route_id, self.default_rule)

    def calculate_fare(
        self,
        route: Route,
        origin: Stop,
        destination: Stop,
        is_concession: bool = False,
        is_transfer: bool = False,
    ) -> float:
        """
        Calculate fare for a single trip segment.

        Args:
            route: The route being traveled
            origin: Starting stop
            destination: Ending stop
            is_concession: Whether passenger has concession card
            is_transfer: Whether this is a transfer (discount applies)

        Returns:
            Fare amount in currency units
        """
        rule = self.get_rule_for_route(route.route_id)

        if rule.fare_type == FareType.FLAT:
            fare = rule.base_fare
        elif rule.fare_type == FareType.ZONE_BASED:
            zones_crossed = abs(destination.zone - origin.zone) + 1
            fare = rule.base_fare + (zones_crossed - 1) * rule.per_zone_charge
        elif rule.fare_type == FareType.DISTANCE_BASED:
            distance = origin.distance_to(destination)
            fare = rule.base_fare + distance * rule.per_km_charge
        else:
            fare = rule.base_fare

        if is_transfer:
            fare *= (1 - rule.transfer_discount)
        if is_concession:
            fare *= (1 - rule.concession_discount)

        fare = max(rule.min_fare, min(fare, rule.max_fare))
        return round(fare, 2)

    def calculate_trip_fare(
        self,
        routes: List[Route],
        stops: List[Stop],
        is_concession: bool = False,
    ) -> float:
        """
        Calculate total fare for a multi-segment trip.

        Args:
            routes: List of routes taken (one per segment)
            stops: List of stops visited in order
            is_concession: Concession card holder

        Returns:
            Total fare for the trip
        """
        if len(routes) == 0 or len(stops) < 2:
            return 0.0

        total = 0.0
        for i, route in enumerate(routes):
            is_transfer = i > 0
            origin = stops[i]
            destination = stops[i + 1] if i + 1 < len(stops) else stops[-1]
            total += self.calculate_fare(route, origin, destination, is_concession, is_transfer)

        return round(total, 2)

    def estimate_daily_pass_savings(
        self, daily_pass_cost: float, routes: List[Route], stops: List[Stop]
    ) -> float:
        """Calculate savings if using a daily pass vs individual fares."""
        individual_fare = self.calculate_trip_fare(routes, stops)
        return round(max(0, individual_fare - daily_pass_cost), 2)
