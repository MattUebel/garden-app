"""Tests for garden bed functionality."""
import pytest
from datetime import date

def test_create_garden_bed(client, test_db):
    response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": "Test notes"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Bed"
    assert data["dimensions"] == "3x6"
    assert "id" in data

def test_list_garden_beds(client, test_db):
    # Create a test bed first
    client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": "Test notes"
    })
    
    response = client.get("/api/garden/beds")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Test Bed"

def test_create_garden_bed_invalid_dimensions(client, test_db):
    response = client.post("/api/garden/beds", json={
        "name": "Invalid Bed",
        "dimensions": "invalid",
        "notes": "Test notes"
    })
    assert response.status_code == 422
    data = response.json()
    assert "dimensions" in str(data["detail"])

def test_plant_dimension_validation(client, test_db):
    invalid_dimensions = ["0x0", "-1x5", "axb", "10", "10x", "x10"]
    
    for dims in invalid_dimensions:
        response = client.post("/api/garden/beds", json={
            "name": "Invalid Bed",
            "dimensions": dims,
            "notes": ""
        })
        assert response.status_code == 422
        data = response.json()
        assert "dimensions" in str(data["detail"])