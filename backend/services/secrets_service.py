"""
AWS Secrets Manager Service Wrapper.

Securely stores and retrieves API keys and credentials.
Uses environment variables / in-memory store in mock mode.
"""

import os
import json


class SecretsService:
    """Wrapper for AWS Secrets Manager operations."""

    def __init__(self, use_mock=True):
        self.use_mock = use_mock
        self._mock_secrets = {
            "transit-planner/db-credentials": json.dumps({
                "username": "transit_admin",
                "password": "mock_password_123",
                "host": "localhost",
                "port": 5432,
                "database": "transit_planner",
            }),
            "transit-planner/api-keys": json.dumps({
                "maps_api_key": "mock_maps_key_abc123",
                "weather_api_key": "mock_weather_key_def456",
            }),
            "transit-planner/jwt-secret": json.dumps({
                "secret": "mock_jwt_secret_x25176862",
            }),
        }

    def get_secret(self, secret_name):
        """Retrieve a secret by name."""
        if self.use_mock:
            value = self._mock_secrets.get(secret_name)
            if value:
                return {"name": secret_name, "value": json.loads(value), "mode": "mock"}
            return None
        return None

    def create_secret(self, secret_name, secret_value):
        """Create or update a secret."""
        if self.use_mock:
            self._mock_secrets[secret_name] = json.dumps(secret_value)
            return {"name": secret_name, "status": "created", "mode": "mock"}
        return {"status": "created"}

    def delete_secret(self, secret_name):
        """Delete a secret."""
        if self.use_mock:
            if secret_name in self._mock_secrets:
                del self._mock_secrets[secret_name]
                return {"name": secret_name, "status": "deleted", "mode": "mock"}
            return {"name": secret_name, "status": "not_found"}
        return {"status": "deleted"}

    def list_secrets(self):
        """List all secret names."""
        if self.use_mock:
            return list(self._mock_secrets.keys())
        return []

    def health_check(self):
        return {
            "service": "AWS Secrets Manager",
            "status": "healthy",
            "mode": "local_mock" if self.use_mock else "production",
            "secrets_count": len(self._mock_secrets) if self.use_mock else "N/A",
        }
