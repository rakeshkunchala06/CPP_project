"""Integration tests for the Schedules CRUD API."""

import pytest


class TestSchedulesAPI:
    """Tests for /api/schedules endpoints."""

    def test_get_schedules_empty(self, client):
        resp = client.get("/api/schedules")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_create_schedule(self, client):
        data = {
            "schedule_id": "SC1",
            "route_id": "R1",
            "stop_id": "S1",
            "departure_time": "08:00",
            "arrival_time": "08:10",
        }
        resp = client.post("/api/schedules", json=data)
        assert resp.status_code == 201

    def test_create_schedule_missing_id(self, client):
        resp = client.post("/api/schedules", json={})
        assert resp.status_code == 400

    def test_update_schedule(self, client):
        data = {"schedule_id": "SC1", "route_id": "R1", "stop_id": "S1",
                "departure_time": "08:00", "arrival_time": "08:10"}
        create_resp = client.post("/api/schedules", json=data)
        sid = create_resp.get_json()["id"]
        resp = client.put(f"/api/schedules/{sid}", json={"departure_time": "09:00"})
        assert resp.status_code == 200
        assert resp.get_json()["departure_time"] == "09:00"

    def test_delete_schedule(self, client):
        data = {"schedule_id": "SC1", "route_id": "R1", "stop_id": "S1",
                "departure_time": "08:00", "arrival_time": "08:10"}
        create_resp = client.post("/api/schedules", json=data)
        sid = create_resp.get_json()["id"]
        resp = client.delete(f"/api/schedules/{sid}")
        assert resp.status_code == 200
