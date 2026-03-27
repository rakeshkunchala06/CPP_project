"""Tests for transitplan.schedule_calc module."""

import pytest
from datetime import time
from transitplan.models import Schedule
from transitplan.schedule_calc import ScheduleCalculator


@pytest.fixture
def schedules():
    return [
        Schedule("SC1", "R1", "S1", time(8, 0), time(8, 10)),
        Schedule("SC2", "R1", "S1", time(8, 30), time(8, 40)),
        Schedule("SC3", "R1", "S1", time(9, 0), time(9, 10)),
        Schedule("SC4", "R2", "S1", time(8, 15), time(8, 25)),
        Schedule("SC5", "R1", "S2", time(8, 10), time(8, 20)),
    ]


class TestScheduleCalculator:
    def test_time_to_minutes(self):
        assert ScheduleCalculator.time_to_minutes(time(1, 30)) == 90.0

    def test_minutes_to_time(self):
        t = ScheduleCalculator.minutes_to_time(150)
        assert t.hour == 2
        assert t.minute == 30

    def test_add_minutes(self):
        result = ScheduleCalculator.add_minutes(time(8, 50), 20)
        assert result.hour == 9
        assert result.minute == 10

    def test_add_minutes_wrap_midnight(self):
        result = ScheduleCalculator.add_minutes(time(23, 50), 30)
        assert result.hour == 0
        assert result.minute == 20

    def test_time_difference(self):
        diff = ScheduleCalculator.time_difference(time(8, 0), time(8, 30))
        assert diff == 30.0

    def test_time_difference_wrap(self):
        diff = ScheduleCalculator.time_difference(time(23, 0), time(1, 0))
        assert diff == 120.0

    def test_find_next_departure(self, schedules):
        result = ScheduleCalculator.find_next_departure(schedules, time(8, 20), "S1")
        assert result is not None
        assert result.schedule_id == "SC2"

    def test_find_next_departure_none(self, schedules):
        result = ScheduleCalculator.find_next_departure(schedules, time(8, 0), "S99")
        assert result is None

    def test_calculate_wait_time(self):
        wait = ScheduleCalculator.calculate_wait_time(time(8, 0), time(8, 15))
        assert wait == 15.0

    def test_estimate_total_journey(self):
        total = ScheduleCalculator.estimate_total_journey_time(5, 30, 2, 5)
        assert total == 45.0  # 5 + 30 + 2*5

    def test_get_schedules_in_range(self, schedules):
        results = ScheduleCalculator.get_schedules_in_range(
            schedules, time(8, 0), time(8, 30), "S1"
        )
        assert len(results) >= 2

    def test_get_schedules_in_range_no_stop_filter(self, schedules):
        results = ScheduleCalculator.get_schedules_in_range(
            schedules, time(8, 0), time(8, 30)
        )
        assert len(results) >= 3

    def test_detect_no_conflicts(self, schedules):
        conflicts = ScheduleCalculator.detect_schedule_conflicts(schedules)
        assert len(conflicts) == 0

    def test_detect_conflicts(self):
        scheds = [
            Schedule("SC1", "R1", "S1", time(8, 0), time(8, 10)),
            Schedule("SC2", "R1", "S1", time(8, 1), time(8, 11)),
        ]
        conflicts = ScheduleCalculator.detect_schedule_conflicts(scheds)
        assert len(conflicts) == 1
