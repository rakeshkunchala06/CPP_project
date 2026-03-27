"""
Formatting utilities for transit data output.
"""

from typing import List, Dict, Optional


class TransitFormatter:
    """Formats transit data for display and export."""

    def format_route_summary(self, route: Dict) -> str:
        """Format a route into a human-readable summary string.

        Args:
            route: Route dict with name, origin, destination, stops, etc.

        Returns:
            Formatted summary string.
        """
        name = route.get("name", "Unknown Route")
        origin = route.get("origin", "?")
        destination = route.get("destination", "?")
        stops = route.get("stops", [])
        distance = route.get("total_distance_km", 0)
        transfers = route.get("num_transfers", 0)
        rating = route.get("accessibilityRating", "N/A")

        lines = [
            f"Route: {name}",
            f"  From: {origin}",
            f"  To: {destination}",
            f"  Stops: {len(stops)}",
            f"  Distance: {distance} km",
            f"  Transfers: {transfers}",
            f"  Accessibility Rating: {rating}/5",
        ]
        return "\n".join(lines)

    def format_station_info(self, station: Dict) -> str:
        """Format station information for display.

        Args:
            station: Station dict with name, address, features, etc.

        Returns:
            Formatted station info string.
        """
        name = station.get("name", "Unknown Station")
        address = station.get("address", "No address")
        features = station.get("accessibilityFeatures", [])
        transit_types = station.get("transitTypes", [])

        lines = [
            f"Station: {name}",
            f"  Address: {address}",
            f"  Transit Types: {', '.join(transit_types) if transit_types else 'None'}",
            f"  Accessibility Features:",
        ]
        if features:
            for f in features:
                label = f.replace("_", " ").title()
                lines.append(f"    - {label}")
        else:
            lines.append("    None listed")
        return "\n".join(lines)

    def format_schedule(self, schedule: Dict) -> str:
        """Format a route schedule for display.

        Args:
            schedule: Dict with 'route_name', 'days', and 'times' list.

        Returns:
            Formatted schedule string.
        """
        route_name = schedule.get("route_name", "Unknown Route")
        days = schedule.get("days", "Daily")
        times = schedule.get("times", [])

        lines = [
            f"Schedule: {route_name}",
            f"  Days: {days}",
            f"  Departures:",
        ]
        if times:
            for t in times:
                lines.append(f"    {t}")
        else:
            lines.append("    No times available")
        return "\n".join(lines)

    def to_csv(self, data: List[Dict], columns: Optional[List[str]] = None) -> str:
        """Convert a list of dicts to CSV string.

        Args:
            data: List of flat dicts.
            columns: Optional ordered list of column names. If None, keys
                     from the first row are used.

        Returns:
            CSV-formatted string.
        """
        if not data:
            return ""

        if columns is None:
            columns = list(data[0].keys())

        lines = [",".join(columns)]
        for row in data:
            values = []
            for col in columns:
                val = str(row.get(col, ""))
                if "," in val or '"' in val or "\n" in val:
                    val = '"' + val.replace('"', '""') + '"'
                values.append(val)
            lines.append(",".join(values))
        return "\n".join(lines)

    def format_accessibility_report(self, summary: Dict) -> str:
        """Format an accessibility summary into a report string.

        Args:
            summary: Dict from AccessibilityChecker.get_accessibility_summary().

        Returns:
            Formatted report string.
        """
        total = summary.get("total_stations", 0)
        avg = summary.get("average_score", 0)
        fully = summary.get("fully_accessible_count", 0)
        counts = summary.get("feature_counts", {})

        lines = [
            "=== Accessibility Report ===",
            f"Total Stations: {total}",
            f"Average Accessibility Score: {avg}/100",
            f"Fully Accessible Stations: {fully}",
            "",
            "Feature Availability:",
        ]
        for feature, count in counts.items():
            label = feature.replace("_", " ").title()
            pct = round((count / total) * 100, 1) if total > 0 else 0
            lines.append(f"  {label}: {count}/{total} ({pct}%)")
        return "\n".join(lines)
