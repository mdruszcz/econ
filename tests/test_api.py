"""Tests for the FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestHealthCheck:
    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestBaseline:
    def test_get_baseline(self):
        response = client.get("/baseline")
        assert response.status_code == 200
        data = response.json()
        assert "indicators" in data
        assert "instruments" in data
        assert len(data["indicators"]["years"]) == 8
        assert len(data["instruments"]) == 10


class TestInstruments:
    def test_get_instruments(self):
        response = client.get("/instruments")
        assert response.status_code == 200
        specs = response.json()
        assert len(specs) == 10
        assert all("key" in s for s in specs)


class TestSimulate:
    def test_simulate_default(self):
        response = client.post("/simulate", json={"instruments": {}})
        assert response.status_code == 200
        data = response.json()
        assert "baseline" in data
        assert "scenario" in data
        assert "convergence" in data
        assert "impacts" in data

    def test_simulate_with_instrument(self):
        response = client.post(
            "/simulate",
            json={"name": "Test", "instruments": {"VIG_X": 1000}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test"
        assert data["instruments"]["VIG_X"] == 1000

    def test_simulate_invalid_instrument(self):
        response = client.post(
            "/simulate",
            json={"instruments": {"INVALID": 42}},
        )
        assert response.status_code == 422


class TestExport:
    def test_export_csv(self):
        response = client.post(
            "/export/csv",
            json={"name": "test", "instruments": {}},
        )
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert len(response.content) > 100

    def test_export_excel(self):
        response = client.post(
            "/export/excel",
            json={"name": "test", "instruments": {}},
        )
        assert response.status_code == 200
        assert "spreadsheet" in response.headers["content-type"]
