"""Integration tests for the Routes CRUD API."""

import json
import pytest


class TestRoutesAPI:
    """Tests for /api/routes endpoints."""

    def test_get_routes_empty(self, client):
        resp = client.get("/api/routes")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_create_route(self, client):
        data = {"route_id": "R1", "name": "DART Southbound", "route_type": "rail"}
        resp = client.post("/api/routes", json=data)
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["route_id"] == "R1"
        assert body["name"] == "DART Southbound"

    def test_create_route_missing_fields(self, client):
        resp = client.post("/api/routes", json={})
        assert resp.status_code == 400

    def test_create_duplicate_route(self, client):
        data = {"route_id": "R1", "name": "Route 1", "route_type": "bus"}
        client.post("/api/routes", json=data)
        resp = client.post("/api/routes", json=data)
        assert resp.status_code == 409

    def test_get_route_by_id(self, client):
        data = {"route_id": "R1", "name": "Route 1", "route_type": "bus"}
        create_resp = client.post("/api/routes", json=data)
        route_id = create_resp.get_json()["id"]
        resp = client.get(f"/api/routes/{route_id}")
        assert resp.status_code == 200
        assert resp.get_json()["route_id"] == "R1"

    def test_get_route_not_found(self, client):
        resp = client.get("/api/routes/999")
        assert resp.status_code == 404

    def test_update_route(self, client):
        data = {"route_id": "R1", "name": "Old Name", "route_type": "bus"}
        create_resp = client.post("/api/routes", json=data)
        route_id = create_resp.get_json()["id"]
        resp = client.put(f"/api/routes/{route_id}", json={"name": "New Name"})
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "New Name"

    def test_delete_route(self, client):
        data = {"route_id": "R1", "name": "Route 1", "route_type": "bus"}
        create_resp = client.post("/api/routes", json=data)
        route_id = create_resp.get_json()["id"]
        resp = client.delete(f"/api/routes/{route_id}")
        assert resp.status_code == 200
        # Verify deleted
        resp = client.get(f"/api/routes/{route_id}")
        assert resp.status_code == 404
