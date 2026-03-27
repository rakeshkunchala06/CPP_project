"""Integration tests for AWS service endpoints."""

import pytest


class TestAWSServicesAPI:
    """Tests for /api/aws endpoints."""

    def test_aws_status(self, client):
        resp = client.get("/api/aws/status")
        assert resp.status_code == 200
        body = resp.get_json()
        assert len(body["services"]) == 7
        for svc in body["services"]:
            assert svc["status"] == "healthy"

    def test_geocode(self, client):
        resp = client.post("/api/aws/geocode", json={"address": "Connolly Station"})
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["latitude"] == 53.3509

    def test_geocode_missing_address(self, client):
        resp = client.post("/api/aws/geocode", json={})
        assert resp.status_code == 400

    def test_sentiment_positive(self, client):
        resp = client.post("/api/aws/sentiment", json={"text": "great excellent service"})
        assert resp.status_code == 200
        assert resp.get_json()["sentiment"] == "POSITIVE"

    def test_sentiment_negative(self, client):
        resp = client.post("/api/aws/sentiment", json={"text": "terrible awful experience"})
        assert resp.status_code == 200
        assert resp.get_json()["sentiment"] == "NEGATIVE"

    def test_sentiment_missing_text(self, client):
        resp = client.post("/api/aws/sentiment", json={})
        assert resp.status_code == 400

    def test_sqs_send_and_receive(self, client):
        resp = client.post("/api/aws/sqs/send", json={"trip": "S1 to S3"})
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "sent"

        resp = client.get("/api/aws/sqs/receive")
        assert resp.status_code == 200
        assert len(resp.get_json()["messages"]) >= 1

    def test_s3_upload_and_list(self, client):
        resp = client.post("/api/aws/s3/upload", json={"key": "test.json", "data": "{}"})
        assert resp.status_code == 200

        resp = client.get("/api/aws/s3/files")
        assert resp.status_code == 200

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_root_endpoint(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        body = resp.get_json()
        assert "x25176862" in body["author"]
