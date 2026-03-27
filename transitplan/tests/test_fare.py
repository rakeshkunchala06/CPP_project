"""Tests for transitplan.fare module."""

import pytest
from transitplan.models import Stop, Route
from transitplan.fare import FareCalculator, FareRule, FareType


@pytest.fixture
def stops():
    return [
        Stop("S1", "Zone 1", 53.35, -6.26, zone=1),
        Stop("S2", "Zone 1", 53.34, -6.25, zone=1),
        Stop("S3", "Zone 2", 53.33, -6.24, zone=2),
        Stop("S4", "Zone 3", 53.32, -6.23, zone=3),
    ]


@pytest.fixture
def calculator():
    return FareCalculator()


class TestFareRule:
    def test_rule_creation(self):
        rule = FareRule("FR1", FareType.FLAT, 2.50)
        assert rule.rule_id == "FR1"
        assert rule.base_fare == 2.50

    def test_rule_to_dict(self):
        rule = FareRule("FR1", FareType.ZONE_BASED, 2.00)
        d = rule.to_dict()
        assert d["fare_type"] == "zone_based"


class TestFareCalculator:
    def test_flat_fare(self, stops):
        rule = FareRule("flat", FareType.FLAT, 3.00)
        calc = FareCalculator(default_rule=rule)
        route = Route("R1", "Test", "bus", stops[:2])
        fare = calc.calculate_fare(route, stops[0], stops[1])
        assert fare == 3.00

    def test_zone_based_same_zone(self, calculator, stops):
        route = Route("R1", "Test", "bus")
        fare = calculator.calculate_fare(route, stops[0], stops[1])
        assert fare == 2.00  # base fare, 1 zone

    def test_zone_based_cross_zone(self, calculator, stops):
        route = Route("R1", "Test", "bus")
        fare = calculator.calculate_fare(route, stops[0], stops[2])
        # base 2.00 + 1 extra zone * 0.50 = 2.50
        assert fare == 2.50

    def test_zone_based_three_zones(self, calculator, stops):
        route = Route("R1", "Test", "bus")
        fare = calculator.calculate_fare(route, stops[0], stops[3])
        # base 2.00 + 2 extra zones * 0.50 = 3.00
        assert fare == 3.00

    def test_transfer_discount(self, calculator, stops):
        route = Route("R1", "Test", "bus")
        fare = calculator.calculate_fare(route, stops[0], stops[1], is_transfer=True)
        assert fare == 1.50  # 2.00 * 0.75

    def test_concession_discount(self, calculator, stops):
        route = Route("R1", "Test", "bus")
        fare = calculator.calculate_fare(route, stops[0], stops[1], is_concession=True)
        assert fare == 1.00  # 2.00 * 0.50

    def test_distance_based(self, stops):
        rule = FareRule("dist", FareType.DISTANCE_BASED, 1.50, per_km_charge=0.20)
        calc = FareCalculator(default_rule=rule)
        route = Route("R1", "Test", "bus")
        fare = calc.calculate_fare(route, stops[0], stops[3])
        assert fare >= rule.min_fare

    def test_trip_fare(self, calculator, stops):
        r1 = Route("R1", "Bus", "bus")
        r2 = Route("R2", "Rail", "rail")
        fare = calculator.calculate_trip_fare([r1, r2], stops[:3])
        assert fare > 0

    def test_empty_trip_fare(self, calculator):
        assert calculator.calculate_trip_fare([], []) == 0.0

    def test_set_route_rule(self, calculator):
        rule = FareRule("custom", FareType.FLAT, 5.00)
        calculator.set_route_rule("R1", rule)
        assert calculator.get_rule_for_route("R1").base_fare == 5.00

    def test_daily_pass_savings(self, calculator, stops):
        r1 = Route("R1", "Bus", "bus")
        savings = calculator.estimate_daily_pass_savings(1.50, [r1], stops[:2])
        # Individual fare is 2.00, daily pass 1.50, savings 0.50
        assert savings == 0.50
