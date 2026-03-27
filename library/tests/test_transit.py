"""
Comprehensive tests for the transit_utils library.
30+ tests covering route, accessibility, formatter, and validator modules.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from transit_utils.route import RouteOptimizer
from transit_utils.accessibility import AccessibilityChecker, KNOWN_FEATURES
from transit_utils.formatter import TransitFormatter
from transit_utils.validator import TransitValidator


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def optimizer():
    return RouteOptimizer()


@pytest.fixture
def checker():
    return AccessibilityChecker()


@pytest.fixture
def formatter():
    return TransitFormatter()


@pytest.fixture
def validator():
    return TransitValidator()


@pytest.fixture
def sample_stations():
    return [
        {
            "name": "Central Station",
            "latitude": 53.3498,
            "longitude": -6.2603,
            "address": "O'Connell St, Dublin",
            "accessibilityFeatures": [
                "wheelchair_ramp", "elevator", "tactile_paving",
                "audio_announcements", "low_floor_boarding", "accessible_toilet",
            ],
            "transitTypes": ["bus", "train"],
        },
        {
            "name": "Park Stop",
            "latitude": 53.3400,
            "longitude": -6.2500,
            "address": "Park Rd, Dublin",
            "accessibilityFeatures": ["wheelchair_ramp", "low_floor_boarding"],
            "transitTypes": ["bus"],
        },
        {
            "name": "University Stop",
            "latitude": 53.3440,
            "longitude": -6.2670,
            "address": "College Green, Dublin",
            "accessibilityFeatures": [],
            "transitTypes": ["tram"],
        },
    ]


@pytest.fixture
def origin():
    return {"name": "Home", "latitude": 53.3500, "longitude": -6.2600}


@pytest.fixture
def destination():
    return {"name": "Office", "latitude": 53.3300, "longitude": -6.2400}


# ---------------------------------------------------------------------------
# RouteOptimizer Tests
# ---------------------------------------------------------------------------

class TestRouteOptimizer:

    def test_calculate_distance_same_point(self, optimizer):
        dist = optimizer.calculate_distance(53.35, -6.26, 53.35, -6.26)
        assert dist == 0.0

    def test_calculate_distance_known(self, optimizer):
        # Dublin to London ~463 km
        dist = optimizer.calculate_distance(53.3498, -6.2603, 51.5074, -0.1278)
        assert 450 < dist < 480

    def test_calculate_distance_positive(self, optimizer):
        dist = optimizer.calculate_distance(0, 0, 1, 1)
        assert dist > 0

    def test_find_routes_empty_stops(self, optimizer, origin, destination):
        routes = optimizer.find_routes(origin, destination, [])
        assert len(routes) == 1  # direct route only
        assert routes[0]["num_transfers"] == 0

    def test_find_routes_with_stops(self, optimizer, origin, destination, sample_stations):
        routes = optimizer.find_routes(origin, destination, sample_stations)
        assert len(routes) == 4  # 1 direct + 3 via stops

    def test_find_routes_sorted_by_distance(self, optimizer, origin, destination, sample_stations):
        routes = optimizer.find_routes(origin, destination, sample_stations)
        distances = [r["total_distance_km"] for r in routes]
        assert distances == sorted(distances)

    def test_find_routes_empty_origin(self, optimizer, destination):
        routes = optimizer.find_routes({}, destination, [])
        assert routes == []

    def test_find_routes_empty_destination(self, optimizer, origin):
        routes = optimizer.find_routes(origin, {}, [])
        assert routes == []

    def test_calculate_travel_time(self, optimizer):
        route = {"total_distance_km": 30, "num_transfers": 2}
        result = optimizer.calculate_travel_time(route)
        assert result["travel_minutes"] == 60.0
        assert result["transfer_minutes"] == 10
        assert result["total_minutes"] == 70.0

    def test_calculate_travel_time_zero_distance(self, optimizer):
        route = {"total_distance_km": 0, "num_transfers": 0}
        result = optimizer.calculate_travel_time(route)
        assert result["total_minutes"] == 0.0

    def test_filter_accessible_routes_no_requirements(self, optimizer):
        routes = [{"stops": []}]
        assert optimizer.filter_accessible_routes(routes, []) == routes

    def test_filter_accessible_routes_filters(self, optimizer, sample_stations):
        routes = [
            {"stops": [sample_stations[0]]},
            {"stops": [sample_stations[1]]},
            {"stops": [sample_stations[2]]},
        ]
        result = optimizer.filter_accessible_routes(routes, ["elevator"])
        assert len(result) == 1

    def test_filter_accessible_routes_direct(self, optimizer):
        routes = [{"stops": []}]
        result = optimizer.filter_accessible_routes(routes, ["elevator"])
        assert len(result) == 1  # direct routes pass

    def test_optimize_route_fastest(self, optimizer):
        route = {"total_distance_km": 10, "num_transfers": 1, "stops": []}
        result = optimizer.optimize_route(route, "fastest")
        assert result["optimization"]["preference"] == "fastest"
        assert "estimated_minutes" in result["optimization"]

    def test_optimize_route_accessible(self, optimizer, sample_stations):
        route = {"total_distance_km": 10, "num_transfers": 1, "stops": [sample_stations[0]]}
        result = optimizer.optimize_route(route, "accessible")
        assert result["optimization"]["preference"] == "accessible"

    def test_optimize_route_least_transfers(self, optimizer):
        route = {"total_distance_km": 10, "num_transfers": 0, "stops": []}
        result = optimizer.optimize_route(route, "least_transfers")
        assert result["optimization"]["score"] == 100

    def test_optimize_route_unknown(self, optimizer):
        route = {"total_distance_km": 5, "num_transfers": 0, "stops": []}
        result = optimizer.optimize_route(route, "scenic")
        assert result["optimization"]["score"] == 0


# ---------------------------------------------------------------------------
# AccessibilityChecker Tests
# ---------------------------------------------------------------------------

class TestAccessibilityChecker:

    def test_check_station_full(self, checker, sample_stations):
        result = checker.check_station_accessibility(sample_stations[0])
        assert result["station"] == "Central Station"
        assert all(result[f] for f in KNOWN_FEATURES)

    def test_check_station_partial(self, checker, sample_stations):
        result = checker.check_station_accessibility(sample_stations[1])
        assert result["wheelchair_ramp"] is True
        assert result["elevator"] is False

    def test_score_full(self, checker, sample_stations):
        assert checker.get_accessibility_score(sample_stations[0]) == 100

    def test_score_partial(self, checker, sample_stations):
        score = checker.get_accessibility_score(sample_stations[1])
        assert 0 < score < 100

    def test_score_none(self, checker, sample_stations):
        assert checker.get_accessibility_score(sample_stations[2]) == 0

    def test_filter_by_features(self, checker, sample_stations):
        result = checker.filter_stations_by_features(sample_stations, ["wheelchair_ramp"])
        assert len(result) == 2

    def test_filter_by_features_empty(self, checker, sample_stations):
        result = checker.filter_stations_by_features(sample_stations, [])
        assert len(result) == 3

    def test_validate_good_data(self, checker):
        data = {"accessibilityFeatures": ["elevator", "wheelchair_ramp"]}
        result = checker.validate_accessibility_data(data)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_missing_field(self, checker):
        result = checker.validate_accessibility_data({})
        assert result["valid"] is False

    def test_validate_unknown_feature(self, checker):
        data = {"accessibilityFeatures": ["jetpack"]}
        result = checker.validate_accessibility_data(data)
        assert result["valid"] is True
        assert len(result["warnings"]) > 0

    def test_summary(self, checker, sample_stations):
        summary = checker.get_accessibility_summary(sample_stations)
        assert summary["total_stations"] == 3
        assert summary["fully_accessible_count"] == 1
        assert summary["average_score"] > 0

    def test_summary_empty(self, checker):
        summary = checker.get_accessibility_summary([])
        assert summary["total_stations"] == 0


# ---------------------------------------------------------------------------
# TransitFormatter Tests
# ---------------------------------------------------------------------------

class TestTransitFormatter:

    def test_format_route_summary(self, formatter):
        route = {
            "name": "Route 1",
            "origin": "A",
            "destination": "B",
            "stops": [],
            "total_distance_km": 5,
            "num_transfers": 0,
            "accessibilityRating": 4,
        }
        text = formatter.format_route_summary(route)
        assert "Route 1" in text
        assert "5 km" in text

    def test_format_station_info(self, formatter, sample_stations):
        text = formatter.format_station_info(sample_stations[0])
        assert "Central Station" in text
        assert "Wheelchair Ramp" in text

    def test_format_schedule(self, formatter):
        schedule = {"route_name": "Red Line", "days": "Mon-Fri", "times": ["08:00", "09:00"]}
        text = formatter.format_schedule(schedule)
        assert "Red Line" in text
        assert "08:00" in text

    def test_to_csv(self, formatter):
        data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        csv = formatter.to_csv(data)
        assert "a,b" in csv
        assert "1,2" in csv

    def test_to_csv_empty(self, formatter):
        assert formatter.to_csv([]) == ""

    def test_to_csv_with_columns(self, formatter):
        data = [{"x": 1, "y": 2, "z": 3}]
        csv = formatter.to_csv(data, columns=["z", "x"])
        assert csv.startswith("z,x")

    def test_format_accessibility_report(self, formatter):
        summary = {
            "total_stations": 3,
            "average_score": 55.6,
            "fully_accessible_count": 1,
            "feature_counts": {"wheelchair_ramp": 2, "elevator": 1},
        }
        report = formatter.format_accessibility_report(summary)
        assert "Accessibility Report" in report
        assert "55.6" in report


# ---------------------------------------------------------------------------
# TransitValidator Tests
# ---------------------------------------------------------------------------

class TestTransitValidator:

    def test_validate_stop_valid(self, validator):
        data = {"name": "Test", "latitude": 53.35, "longitude": -6.26}
        valid, errors = validator.validate_stop(data)
        assert valid is True

    def test_validate_stop_missing_name(self, validator):
        data = {"latitude": 53.35, "longitude": -6.26}
        valid, errors = validator.validate_stop(data)
        assert valid is False

    def test_validate_stop_bad_lat(self, validator):
        data = {"name": "X", "latitude": 999, "longitude": 0}
        valid, errors = validator.validate_stop(data)
        assert valid is False

    def test_validate_stop_bad_feature(self, validator):
        data = {"name": "X", "latitude": 0, "longitude": 0, "accessibilityFeatures": ["jetpack"]}
        valid, errors = validator.validate_stop(data)
        assert valid is False

    def test_validate_route_valid(self, validator):
        data = {"name": "R1", "origin": "A", "destination": "B", "stops": []}
        valid, errors = validator.validate_route(data)
        assert valid is True

    def test_validate_route_same_origin_dest(self, validator):
        data = {"name": "R1", "origin": "A", "destination": "A", "stops": []}
        valid, errors = validator.validate_route(data)
        assert valid is False

    def test_validate_search_valid(self, validator):
        data = {"origin": "A", "destination": "B", "accessibilityNeeds": ["elevator"]}
        valid, errors = validator.validate_search(data)
        assert valid is True

    def test_validate_search_missing_origin(self, validator):
        data = {"destination": "B"}
        valid, errors = validator.validate_search(data)
        assert valid is False

    def test_sanitize_input(self, validator):
        assert validator.sanitize_input("  hello  world  ") == "hello world"

    def test_sanitize_input_script(self, validator):
        result = validator.sanitize_input("<script>alert('x')</script>")
        assert "<" not in result
        assert ">" not in result

    def test_sanitize_input_non_string(self, validator):
        assert validator.sanitize_input(123) == ""
