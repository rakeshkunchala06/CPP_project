"""
Schedule calculation utilities for transit planning.

Handles time arithmetic, wait time estimation, next departure lookups,
and schedule conflict detection.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple
from datetime import time, timedelta

from transitplan.models import Schedule


class ScheduleCalculator:
    """Utilities for working with transit schedules and time calculations."""

    @staticmethod
    def time_to_minutes(t: time) -> float:
        """Convert a time object to minutes since midnight."""
        return t.hour * 60 + t.minute + t.second / 60

    @staticmethod
    def minutes_to_time(minutes: float) -> time:
        """Convert minutes since midnight to a time object."""
        minutes = int(minutes) % (24 * 60)
        hours = minutes // 60
        mins = minutes % 60
        return time(hour=hours, minute=mins)

    @staticmethod
    def add_minutes(t: time, minutes: float) -> time:
        """Add minutes to a time, wrapping past midnight."""
        total = ScheduleCalculator.time_to_minutes(t) + minutes
        return ScheduleCalculator.minutes_to_time(total)

    @staticmethod
    def time_difference(t1: time, t2: time) -> float:
        """
        Calculate difference in minutes between t2 and t1.
        Handles midnight wraparound.
        """
        m1 = ScheduleCalculator.time_to_minutes(t1)
        m2 = ScheduleCalculator.time_to_minutes(t2)
        diff = m2 - m1
        if diff < 0:
            diff += 24 * 60
        return diff

    @staticmethod
    def find_next_departure(
        schedules: List[Schedule], current_time: time, stop_id: str
    ) -> Optional[Schedule]:
        """
        Find the next scheduled departure from a stop after the given time.

        Args:
            schedules: List of schedules to search
            current_time: Current time
            stop_id: Stop to search departures for

        Returns:
            The next Schedule, or None if no departures found
        """
        current_min = ScheduleCalculator.time_to_minutes(current_time)
        candidates = [
            s for s in schedules
            if s.stop_id == stop_id and s.is_active
        ]
        if not candidates:
            return None

        # Find first departure after current_time
        best: Optional[Schedule] = None
        best_wait = float("inf")
        for sched in candidates:
            dep_min = ScheduleCalculator.time_to_minutes(sched.departure_time)
            wait = dep_min - current_min
            if wait < 0:
                wait += 24 * 60
            if wait < best_wait:
                best_wait = wait
                best = sched
        return best

    @staticmethod
    def calculate_wait_time(current_time: time, departure_time: time) -> float:
        """Calculate wait time in minutes until a departure."""
        return ScheduleCalculator.time_difference(current_time, departure_time)

    @staticmethod
    def estimate_total_journey_time(
        wait_minutes: float,
        travel_minutes: float,
        transfer_count: int,
        transfer_wait_minutes: float = 5.0,
    ) -> float:
        """
        Estimate total journey time including waits and transfers.

        Args:
            wait_minutes: Initial wait at origin
            travel_minutes: Total time on vehicles
            transfer_count: Number of transfers
            transfer_wait_minutes: Average wait per transfer

        Returns:
            Total estimated journey time in minutes
        """
        return wait_minutes + travel_minutes + (transfer_count * transfer_wait_minutes)

    @staticmethod
    def get_schedules_in_range(
        schedules: List[Schedule],
        start_time: time,
        end_time: time,
        stop_id: Optional[str] = None,
    ) -> List[Schedule]:
        """
        Get all schedules with departures within a time range.
        """
        start_min = ScheduleCalculator.time_to_minutes(start_time)
        end_min = ScheduleCalculator.time_to_minutes(end_time)
        results = []
        for s in schedules:
            if stop_id and s.stop_id != stop_id:
                continue
            if not s.is_active:
                continue
            dep_min = ScheduleCalculator.time_to_minutes(s.departure_time)
            if start_min <= end_min:
                if start_min <= dep_min <= end_min:
                    results.append(s)
            else:
                # Wraps midnight
                if dep_min >= start_min or dep_min <= end_min:
                    results.append(s)
        return results

    @staticmethod
    def detect_schedule_conflicts(schedules: List[Schedule], min_gap_minutes: float = 2.0) -> List[Tuple[Schedule, Schedule]]:
        """
        Detect scheduling conflicts where two departures from the same stop
        on the same route are too close together.
        """
        conflicts = []
        # Group by (route_id, stop_id)
        groups = {}
        for s in schedules:
            key = (s.route_id, s.stop_id)
            if key not in groups:
                groups[key] = []
            groups[key].append(s)

        for key, group in groups.items():
            sorted_group = sorted(group, key=lambda x: ScheduleCalculator.time_to_minutes(x.departure_time))
            for i in range(len(sorted_group) - 1):
                gap = ScheduleCalculator.time_difference(
                    sorted_group[i].departure_time,
                    sorted_group[i + 1].departure_time,
                )
                if gap < min_gap_minutes:
                    conflicts.append((sorted_group[i], sorted_group[i + 1]))
        return conflicts
