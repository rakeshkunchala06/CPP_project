"""Integration tests for the Stops CRUD API."""

import pytest


class TestStopsAPI:
    """Tests for /api/stops endpoints."""

    def test_get_stops_empty(self, client):
        resp = client.get("/api/stops")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_create_stop(self, client):
        data = {"stop_id": "S1", "name": "Connolly", "latitude": 53.35, "longitude": -6.25}
        resp = client.post("/api/stops", json=data)
        assert resp.status_code == 201
        assert resp.get_json()["name"] == "Connolly"

    def test_create_stop_missing_fields(self, client):
        resp = client.post("/api/stops", json={})
        assert resp.status_code == 400

    def test_create_duplicate_stop(self, client):
        data = {"stop_id": "S1", "name": "Stop 1", "latitude": 0, "longitude": 0}
        client.post("/api/stops", json=data)
        resp = client.post("/api/stops", json=data)
        assert resp.status_code == 409

    def test_get_stop_by_id(self, client):
        data = {"stop_id": "S1", "name": "Stop 1", "latitude": 0, "longitude": 0}
        create_resp = client.post("/api/stops", json=data)
        sid = create_resp.get_json()["id"]
        resp = client.get(f"/api/stops/{sid}")
        assert resp.status_code == 200

    def test_update_stop(self, client):
        data = {"stop_id": "S1", "name": "Old", "latitude": 0, "longitude": 0}
        create_resp = client.post("/api/stops", json=data)
        sid = create_resp.get_json()["id"]
        resp = client.put(f"/api/stops/{sid}", json={"name": "New"})
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "New"

    def test_delete_stop(self, client):
        data = {"stop_id": "S1", "name": "Stop 1", "latitude": 0, "longitude": 0}
        create_resp = client.post("/api/stops", json=data)
        sid = create_resp.get_json()["id"]
        resp = client.delete(f"/api/stops/{sid}")
        assert resp.status_code == 200
