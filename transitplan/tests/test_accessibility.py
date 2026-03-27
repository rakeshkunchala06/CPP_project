"""Tests for transitplan.accessibility module."""

import pytest
from transitplan.models import Stop, Route
from transitplan.accessibility import (
    AccessibilityFeature, AccessibilityType, AccessibilityScorer,
)


@pytest.fixture
def fully_accessible_stop():
    return Stop("S1", "Full Access", 53.35, -6.26, True, True, True, True)


@pytest.fixture
def no_access_stop():
    return Stop("S2", "No Access", 53.34, -6.25, False, False, False, False)


@pytest.fixture
def partial_stop():
    return Stop("S3", "Partial", 53.33, -6.24, True, False, True, False)


@pytest.fixture
def scorer():
    return AccessibilityScorer()


class TestAccessibilityFeature:
    def test_feature_creation(self):
        f = AccessibilityFeature("F1", AccessibilityType.WHEELCHAIR, "Ramp at entrance")
        assert f.feature_id == "F1"
        assert f.is_available is True

    def test_feature_to_dict(self):
        f = AccessibilityFeature("F1", AccessibilityType.AUDIO, "PA system")
        d = f.to_dict()
        assert d["feature_type"] == "audio"


class TestAccessibilityScorer:
    def test_full_score(self, scorer, fully_accessible_stop):
        score = scorer.score_stop(fully_accessible_stop)
        assert score == 1.0

    def test_zero_score(self, scorer, no_access_stop):
        score = scorer.score_stop(no_access_stop)
        assert score == 0.0

    def test_partial_score(self, scorer, partial_stop):
        score = scorer.score_stop(partial_stop)
        assert 0 < score < 1
        # wheelchair (0.4) + visual (0.2) = 0.6
        assert score == 0.6

    def test_score_route(self, scorer, fully_accessible_stop, no_access_stop):
        route = Route("R1", "Test", "bus", [fully_accessible_stop, no_access_stop])
        score = scorer.score_route(route)
        assert score == 0.5

    def test_score_empty_route(self, scorer):
        route = Route("R1", "Empty", "bus", [])
        assert scorer.score_route(route) == 0.0

    def test_score_trip(self, scorer, fully_accessible_stop, partial_stop):
        score = scorer.score_trip([fully_accessible_stop, partial_stop])
        # Min of 1.0 and 0.6 = 0.6
        assert score == 0.6

    def test_score_empty_trip(self, scorer):
        assert scorer.score_trip([]) == 0.0

    def test_get_report(self, scorer, partial_stop):
        report = scorer.get_accessibility_report(partial_stop)
        assert report["overall_score"] == 0.6
        assert len(report["recommendations"]) > 0

    def test_full_access_report_recommendations(self, scorer, fully_accessible_stop):
        report = scorer.get_accessibility_report(fully_accessible_stop)
        assert "meets all accessibility criteria" in report["recommendations"][0]

    def test_filter_accessible_routes(self, scorer, fully_accessible_stop, no_access_stop):
        r1 = Route("R1", "Good", "bus", [fully_accessible_stop])
        r2 = Route("R2", "Bad", "bus", [no_access_stop])
        filtered = scorer.filter_accessible_routes([r1, r2], min_score=0.5)
        assert len(filtered) == 1

    def test_rank_routes(self, scorer, fully_accessible_stop, partial_stop, no_access_stop):
        r1 = Route("R1", "Full", "bus", [fully_accessible_stop])
        r2 = Route("R2", "None", "bus", [no_access_stop])
        r3 = Route("R3", "Partial", "bus", [partial_stop])
        ranked = scorer.rank_routes_by_accessibility([r2, r3, r1])
        assert ranked[0].route_id == "R1"
        assert ranked[-1].route_id == "R2"

    def test_custom_weights(self, fully_accessible_stop):
        custom = {"wheelchair": 0.5, "audio": 0.2, "visual": 0.2, "tactile": 0.1}
        scorer = AccessibilityScorer(custom_weights=custom)
        score = scorer.score_stop(fully_accessible_stop)
        assert score == 1.0
