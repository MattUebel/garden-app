"""Tests for garden route error handling and edge cases."""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

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

def test_update_garden_bed(client, test_db):
    # Create a test bed first
    create_response = client.post("/api/garden/beds", json={
        "name": "Original Bed",
        "dimensions": "3x6",
        "notes": "Original notes"
    })
    bed_id = create_response.json()["id"]
    
    # Update the bed
    update_response = client.patch(f"/api/garden/beds/{bed_id}", json={
        "name": "Updated Bed",
        "dimensions": "4x8",
        "notes": "Updated notes"
    })
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Bed"
    assert data["dimensions"] == "4x8"
    assert data["notes"] == "Updated notes"

def test_update_nonexistent_bed(client, test_db):
    response = client.patch("/api/garden/beds/999", json={
        "name": "Updated Bed",
        "dimensions": "4x8",
        "notes": "Updated notes"
    })
    assert response.status_code == 404

def test_plant_with_quantity(client, test_db):
    # Create a garden bed first
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    # Create a plant with quantity
    plant_response = client.post("/api/garden/plants", json={
        "name": "Tomato",
        "location": f"Bed {bed_id}",
        "planting_date": date.today().isoformat(),
        "status": "PLANTED",
        "season": "SUMMER",
        "quantity": 3
    })
    assert plant_response.status_code == 200
    data = plant_response.json()
    assert data["quantity"] == 3

def test_plant_with_invalid_quantity(client, test_db):
    # Create a garden bed first
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    # Try to create a plant with invalid quantity
    plant_response = client.post("/api/garden/plants", json={
        "name": "Tomato",
        "location": f"Bed {bed_id}",
        "planting_date": date.today().isoformat(),
        "status": "PLANTED",
        "season": "SUMMER",
        "quantity": 0  # Invalid quantity
    })
    assert plant_response.status_code == 422
    data = plant_response.json()
    assert "quantity" in str(data["detail"])

def test_create_garden_bed_db_error(client, test_db, monkeypatch):
    def mock_commit(self):
        raise SQLAlchemyError("Database error")
        
    from sqlalchemy.orm import Session
    monkeypatch.setattr(Session, "commit", mock_commit)
    
    response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": "Test notes"
    })
    assert response.status_code == 500
    assert "Database" in response.json()["detail"]

def test_list_garden_beds_db_error(client, test_db, monkeypatch):
    def mock_query(*args, **kwargs):
        raise SQLAlchemyError("Database error")
        
    from sqlalchemy.orm import Session
    monkeypatch.setattr(Session, "query", mock_query)
    
    response = client.get("/api/garden/beds")
    assert response.status_code == 500

def test_create_plant_invalid_bed_format(client, test_db):
    response = client.post("/api/garden/plants", json={
        "name": "Test Plant",
        "variety": "Test",
        "planting_date": str(date.today()),
        "location": "Invalid Location",  # Wrong format
        "status": "PLANTED",
        "season": "SUMMER",
        "notes": ""
    })
    assert response.status_code == 404
    assert "Invalid location" in response.json()["detail"]

def test_get_nonexistent_plant(client, test_db):
    response = client.get("/api/garden/plants/999")
    assert response.status_code == 404
    assert "Plant not found" in response.json()["detail"]

def test_update_plant_status_invalid_transition_path(client, test_db):
    # Create bed and plant
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    plant_response = client.post("/api/garden/plants", json={
        "name": "Test Plant",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "season": "SUMMER",
        "notes": ""
    })
    plant_id = plant_response.json()["id"]
    
    # Try to skip from PLANTED to FLOWERING (invalid transition)
    response = client.patch(f"/api/garden/plants/{plant_id}/status", json={"new_status": "FLOWERING"})
    assert response.status_code == 400
    assert "Invalid status transition" in response.json()["detail"]
    
    # Try valid transition to SPROUTED
    response = client.patch(f"/api/garden/plants/{plant_id}/status", json={"new_status": "SPROUTED"})
    assert response.status_code == 200
    assert response.json()["status"] == "SPROUTED"
    
    # Try going back to PLANTED (invalid transition)
    response = client.patch(f"/api/garden/plants/{plant_id}/status", json={"new_status": "PLANTED"})
    assert response.status_code == 400
    assert "Invalid status transition" in response.json()["detail"]

def test_update_plant_with_invalid_data(client, test_db):
    # Create bed and plant first
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    plant_response = client.post("/api/garden/plants", json={
        "name": "Test Plant",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "season": "SUMMER",
        "quantity": 1,
        "notes": ""
    })
    plant_id = plant_response.json()["id"]
    
    # Try to update with invalid quantity
    update_data = {
        "name": "Updated Plant",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "season": "SUMMER",
        "quantity": -1,  # Invalid quantity
        "notes": ""
    }
    response = client.patch(f"/api/garden/plants/{plant_id}", json=update_data)
    assert response.status_code == 422