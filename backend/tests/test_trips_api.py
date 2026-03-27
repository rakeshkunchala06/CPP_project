"""Integration tests for the Trips CRUD API."""

import pytest


class TestTripsAPI:
    """Tests for /api/trips endpoints."""

    def test_get_trips_empty(self, client):
        resp = client.get("/api/trips")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_create_trip(self, client):
        data = {
            "trip_id": "T1",
            "origin_stop_id": "S1",
            "destination_stop_id": "S3",
            "strategy": "shortest",
        }
        resp = client.post("/api/trips", json=data)
        assert resp.status_code == 201
        assert resp.get_json()["trip_id"] == "T1"

    def test_create_trip_missing_id(self, client):
        resp = client.post("/api/trips", json={})
        assert resp.status_code == 400

    def test_update_trip(self, client):
        data = {"trip_id": "T1", "origin_stop_id": "S1", "destination_stop_id": "S3"}
        create_resp = client.post("/api/trips", json=data)
        tid = create_resp.get_json()["id"]
        resp = client.put(f"/api/trips/{tid}", json={"status": "completed"})
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "completed"

    def test_delete_trip(self, client):
        data = {"trip_id": "T1", "origin_stop_id": "S1", "destination_stop_id": "S3"}
        create_resp = client.post("/api/trips", json=data)
        tid = create_resp.get_json()["id"]
        resp = client.delete(f"/api/trips/{tid}")
        assert resp.status_code == 200
