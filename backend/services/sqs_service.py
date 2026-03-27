"""
Amazon SQS Service Wrapper.

Manages trip planning request queue for async processing.
Uses in-memory queue in mock mode.
"""

import json
import uuid
from datetime import datetime
from collections import deque


class SQSService:
    """Wrapper for Amazon SQS operations."""

    def __init__(self, use_mock=True, queue_url=None):
        self.use_mock = use_mock
        self.queue_url = queue_url or "http://localhost:4566/queue/trip-planning"
        self._mock_queue = deque()
        self._processed = []

    def send_message(self, message_body):
        """Send a message to the SQS queue."""
        if self.use_mock:
            msg_id = str(uuid.uuid4())
            self._mock_queue.append({
                "message_id": msg_id,
                "body": message_body,
                "timestamp": datetime.utcnow().isoformat(),
            })
            return {"message_id": msg_id, "status": "sent", "mode": "mock"}
        return {"status": "sent"}

    def receive_messages(self, max_messages=10):
        """Receive messages from the queue."""
        if self.use_mock:
            messages = []
            for _ in range(min(max_messages, len(self._mock_queue))):
                messages.append(self._mock_queue.popleft())
            return messages
        return []

    def delete_message(self, receipt_handle):
        """Delete a message from the queue after processing."""
        if self.use_mock:
            self._processed.append(receipt_handle)
            return {"status": "deleted", "mode": "mock"}
        return {"status": "deleted"}

    def get_queue_size(self):
        """Get the number of messages in the queue."""
        if self.use_mock:
            return len(self._mock_queue)
        return 0

    def purge_queue(self):
        """Remove all messages from the queue."""
        if self.use_mock:
            self._mock_queue.clear()
            return {"status": "purged", "mode": "mock"}
        return {"status": "purged"}

    def health_check(self):
        return {
            "service": "Amazon SQS",
            "status": "healthy",
            "mode": "local_mock" if self.use_mock else "production",
            "queue_url": self.queue_url,
            "queue_size": self.get_queue_size(),
        }
