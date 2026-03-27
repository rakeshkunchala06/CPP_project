"""Tests for transitplan.planner module."""

import pytest
from transitplan.models import Stop, Route, TransitNetwork
from transitplan.planner import TripPlanner, TripResult, TripSegment


@pytest.fixture
def network():
    stops = [
        Stop("S1", "Start", 53.35, -6.26),
        Stop("S2", "Middle", 53.34, -6.25),
        Stop("S3", "End", 53.33, -6.24),
        Stop("S4", "Branch", 53.34, -6.23),
    ]
    net = TransitNetwork()
    r1 = Route("R1", "Main Line", "rail", [stops[0], stops[1], stops[2]])
    r2 = Route("R2", "Branch Line", "bus", [stops[1], stops[3]])
    net.add_route(r1)
    net.add_route(r2)
    net.build_connections_from_routes()
    return net


@pytest.fixture
def planner(network):
    return TripPlanner(network)


class TestTripPlanner:
    def test_plan_shortest_direct(self, planner):
        result = planner.plan_trip("S1", "S3", "shortest")
        assert result is not None
        assert result.is_valid
        assert result.total_minutes > 0

    def test_plan_same_origin_destination(self, planner):
        result = planner.plan_trip("S1", "S1")
        assert result is not None
        assert not result.is_valid
        assert result.total_minutes == 0

    def test_plan_invalid_origin(self, planner):
        result = planner.plan_trip("FAKE", "S3")
        assert result is None

    def test_plan_invalid_destination(self, planner):
        result = planner.plan_trip("S1", "FAKE")
        assert result is None

    def test_plan_with_transfer(self, planner):
        result = planner.plan_trip("S1", "S4", "shortest")
        assert result is not None
        assert result.is_valid
        assert result.total_transfers >= 1

    def test_fewest_transfers_strategy(self, planner):
        result = planner.plan_trip("S1", "S4", "fewest_transfers")
        assert result is not None
        assert result.is_valid

    def test_find_all_paths(self, planner):
        results = planner.find_all_paths("S1", "S3")
        assert len(results) >= 1

    def test_trip_result_to_dict(self, planner):
        result = planner.plan_trip("S1", "S3")
        d = result.to_dict()
        assert "origin" in d
        assert "segments" in d
        assert "total_minutes" in d


class TestTripResult:
    def test_empty_trip_not_valid(self):
        s = Stop("S1", "A", 0, 0)
        result = TripResult(origin=s, destination=s)
        assert not result.is_valid

    def test_add_segment_increments_transfers(self):
        s1 = Stop("S1", "A", 0, 0)
        s2 = Stop("S2", "B", 0, 0)
        s3 = Stop("S3", "C", 0, 0)
        r1 = Route("R1", "R1", "bus")
        r2 = Route("R2", "R2", "bus")
        result = TripResult(origin=s1, destination=s3)
        seg1 = TripSegment(r1, s1, s2, 10, "08:00", "08:10")
        seg2 = TripSegment(r2, s2, s3, 5, "08:15", "08:20")
        result.add_segment(seg1)
        assert result.total_transfers == 0
        result.add_segment(seg2)
        assert result.total_transfers == 1
        assert result.total_minutes == 15
