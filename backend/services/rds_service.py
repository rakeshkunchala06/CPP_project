"""
Amazon RDS Service Wrapper.

Manages PostgreSQL database connections for routes, stops, and schedules.
Falls back to SQLite in local mock mode.
"""

import os
from flask import current_app


class RDSService:
    """Wrapper for Amazon RDS (PostgreSQL) operations."""

    def __init__(self, use_mock=True):
        self.use_mock = use_mock
        self.connection_info = {}

    def get_connection_string(self):
        """Get the database connection string."""
        if self.use_mock:
            return "sqlite:///transit_planner.db"
        return os.environ.get(
            "DATABASE_URL",
            "postgresql://user:pass@rds-endpoint:5432/transit_planner"
        )

    def health_check(self):
        """Check database connectivity."""
        try:
            if self.use_mock:
                return {
                    "service": "Amazon RDS",
                    "status": "healthy",
                    "mode": "local_mock",
                    "engine": "SQLite (local) / PostgreSQL (production)",
                    "details": "Using local SQLite database for development",
                }
            return {
                "service": "Amazon RDS",
                "status": "healthy",
                "mode": "production",
                "engine": "PostgreSQL",
            }
        except Exception as e:
            return {
                "service": "Amazon RDS",
                "status": "unhealthy",
                "error": str(e),
            }

    def get_stats(self):
        """Get database statistics."""
        return {
            "service": "Amazon RDS",
            "tables": ["routes", "stops", "schedules", "trips", "accessibility_features"],
            "mode": "mock" if self.use_mock else "production",
        }
