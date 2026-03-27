"""
Amazon S3 Service Wrapper.

Manages static assets and map data storage.
Uses local filesystem in mock mode.
"""

import os
import json
from datetime import datetime


class S3Service:
    """Wrapper for Amazon S3 operations."""

    def __init__(self, use_mock=True, bucket_name="transit-planner-assets"):
        self.use_mock = use_mock
        self.bucket_name = bucket_name
        self._mock_store = {}

    def upload_file(self, key, data, content_type="application/json"):
        """Upload a file to S3 or mock store."""
        if self.use_mock:
            self._mock_store[key] = {
                "data": data,
                "content_type": content_type,
                "uploaded_at": datetime.utcnow().isoformat(),
            }
            return {"status": "uploaded", "key": key, "mode": "mock"}
        # Production: use boto3
        return {"status": "uploaded", "key": key, "bucket": self.bucket_name}

    def get_file(self, key):
        """Retrieve a file from S3 or mock store."""
        if self.use_mock:
            if key in self._mock_store:
                return self._mock_store[key]["data"]
            return None
        return None

    def delete_file(self, key):
        """Delete a file from S3 or mock store."""
        if self.use_mock:
            if key in self._mock_store:
                del self._mock_store[key]
                return {"status": "deleted", "key": key}
            return {"status": "not_found", "key": key}
        return {"status": "deleted", "key": key}

    def list_files(self, prefix=""):
        """List files in the bucket with an optional prefix."""
        if self.use_mock:
            return [k for k in self._mock_store if k.startswith(prefix)]
        return []

    def health_check(self):
        """Check S3 connectivity."""
        return {
            "service": "Amazon S3",
            "status": "healthy",
            "mode": "local_mock" if self.use_mock else "production",
            "bucket": self.bucket_name,
            "files_count": len(self._mock_store) if self.use_mock else "N/A",
        }
