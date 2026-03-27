"""Tests for transitplan.models module."""

import pytest
from datetime import time
from transitplan.models import Stop, Route, Schedule, Connection, TransitNetwork


@pytest.fixture
def sample_stops():
    return [
        Stop("S1", "Connolly Station", 53.3509, -6.2500, True, True, True, True, 1),
        Stop("S2", "Tara Street", 53.3475, -6.2545, True, True, True, False, 1),
        Stop("S3", "Pearse Station", 53.3435, -6.2480, True, False, True, False, 2),
        Stop("S4", "Grand Canal Dock", 53.3395, -6.2390, False, False, False, False, 2),
        Stop("S5", "Lansdowne Road", 53.3340, -6.2280, True, True, False, True, 3),
    ]


@pytest.fixture
def sample_route(sample_stops):
    return Route("R1", "DART Southbound", "rail", sample_stops[:3], color="#00AA00")


@pytest.fixture
def sample_network(sample_stops):
    net = TransitNetwork()
    r1 = Route("R1", "DART South", "rail", sample_stops[:3])
    r2 = Route("R2", "Bus 4", "bus", [sample_stops[1], sample_stops[3], sample_stops[4]])
    net.add_route(r1)
    net.add_route(r2)
    net.build_connections_from_routes()
    return net


class TestStop:
    def test_stop_creation(self, sample_stops):
        s = sample_stops[0]
        assert s.stop_id == "S1"
        assert s.name == "Connolly Station"
        assert s.wheelchair_accessible is True

    def test_distance_to(self, sample_stops):
        d = sample_stops[0].distance_to(sample_stops[1])
        assert d > 0
        assert d < 10  # Should be less than 10km within Dublin

    def test_distance_to_self(self, sample_stops):
        d = sample_stops[0].distance_to(sample_stops[0])
        assert d == 0.0

    def test_stop_to_dict(self, sample_stops):
        d = sample_stops[0].to_dict()
        assert d["stop_id"] == "S1"
        assert "latitude" in d


class TestRoute:
    def test_route_creation(self, sample_route):
        assert sample_route.route_id == "R1"
        assert len(sample_route.stops) == 3

    def test_add_stop(self, sample_route, sample_stops):
        sample_route.add_stop(sample_stops[3])
        assert len(sample_route.stops) == 4

    def test_remove_stop(self, sample_route):
        result = sample_route.remove_stop("S2")
        assert result is True
        assert len(sample_route.stops) == 2

    def test_remove_nonexistent_stop(self, sample_route):
        result = sample_route.remove_stop("FAKE")
        assert result is False

    def test_get_stop_ids(self, sample_route):
        ids = sample_route.get_stop_ids()
        assert ids == ["S1", "S2", "S3"]

    def test_total_distance(self, sample_route):
        d = sample_route.total_distance()
        assert d > 0


class TestSchedule:
    def test_schedule_duration(self):
        s = Schedule("SC1", "R1", "S1", time(8, 0), time(8, 15))
        assert s.duration_minutes() == 15.0

    def test_schedule_to_dict(self):
        s = Schedule("SC1", "R1", "S1", time(8, 0), time(8, 15))
        d = s.to_dict()
        assert d["schedule_id"] == "SC1"


class TestTransitNetwork:
    def test_add_stop(self):
        net = TransitNetwork()
        s = Stop("S1", "Test", 0, 0)
        net.add_stop(s)
        assert "S1" in net.stops

    def test_add_route_registers_stops(self, sample_stops):
        net = TransitNetwork()
        r = Route("R1", "Test", "bus", sample_stops[:2])
        net.add_route(r)
        assert "S1" in net.stops
        assert "S2" in net.stops

    def test_build_connections(self, sample_network):
        assert len(sample_network.connections) > 0

    def test_get_neighbors(self, sample_network):
        neighbors = sample_network.get_neighbors("S1")
        assert len(neighbors) >= 1

    def test_find_transfer_points(self, sample_network):
        transfers = sample_network.find_transfer_points()
        # S2 (Tara Street) is on both R1 and R2
        transfer_ids = [s.stop_id for s in transfers]
        assert "S2" in transfer_ids

    def test_get_routes_for_stop(self, sample_network):
        routes = sample_network.get_routes_for_stop("S2")
        assert len(routes) == 2

    def test_network_to_dict(self, sample_network):
        d = sample_network.to_dict()
        assert "stops" in d
        assert "routes" in d
        assert "transfer_points" in d
