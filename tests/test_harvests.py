"""Tests for harvest tracking functionality.

This module contains tests for the harvest tracking features of the garden app, including:
- Adding harvests to plants in valid states (FLOWERING/HARVESTING)
- Validation of harvest data
- Listing and deleting harvest records
- State transitions when harvests are added

Each test uses a fresh database instance provided by the test_db fixture.
"""
from datetime import date, datetime
import pytest
from fastapi.testclient import TestClient

def test_add_harvest(client, test_db):
    """Test adding a harvest record to a plant.
    
    Verifies:
    - Plant can progress through states to FLOWERING
    - Harvest can be added successfully
    - Plant transitions to HARVESTING state after first harvest
    """
    # Create bed and plant
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    plant_response = client.post("/api/garden/plants", json={
        "name": "Test Plant",
        "variety": "Test",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "quantity": 1,
        "expected_harvest_date": str(date.today()),
        "notes": ""
    })
    plant_id = plant_response.json()["id"]

    # Progress plant to FLOWERING
    for status in ["SPROUTED", "FLOWERING"]:
        response = client.patch(f"/api/garden/plants/{plant_id}/status", json={"new_status": status})
        assert response.status_code == 200

    # Add first harvest - should transition to HARVESTING
    harvest_data = {
        "plant_id": plant_id,
        "harvest_date": str(date.today()),
        "quantity": 2.5,
        "unit": "lbs",
        "notes": "First harvest"
    }
    response = client.post(f"/api/garden/plants/{plant_id}/harvests", json=harvest_data)
    assert response.status_code == 200
    
    # Verify plant status changed to HARVESTING
    plant_response = client.get(f"/api/garden/plants/{plant_id}")
    assert plant_response.json()["status"] == "HARVESTING"

def test_harvest_invalid_status(client, test_db):
    """Test that harvests are only allowed for FLOWERING/HARVESTING plants.
    
    Verifies:
    - Attempt to add harvest to PLANTED plant fails
    - Appropriate error message is returned
    """
    # Create bed and plant
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    plant_response = client.post("/api/garden/plants", json={
        "name": "Test Plant",
        "variety": "Test",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "quantity": 1,
        "expected_harvest_date": str(date.today()),
        "notes": ""
    })
    plant_id = plant_response.json()["id"]

    # Try to harvest while PLANTED
    harvest_data = {
        "plant_id": plant_id,
        "harvest_date": str(date.today()),
        "quantity": 2.5,
        "unit": "lbs",
        "notes": "Should fail"
    }
    response = client.post(f"/api/garden/plants/{plant_id}/harvests", json=harvest_data)
    assert response.status_code == 400
    assert "Plant must be FLOWERING or HARVESTING" in response.json()["detail"]

def test_list_harvests(client, test_db):
    """Test listing all harvests for a plant.
    
    Verifies:
    - Multiple harvests can be added to a single plant
    - All harvests are returned when listing
    - Harvest quantities are recorded correctly
    """
    # Create bed and plant
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    plant_response = client.post("/api/garden/plants", json={
        "name": "Test Plant",
        "variety": "Test",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "FLOWERING",  # Start in FLOWERING state
        "quantity": 1,
        "expected_harvest_date": str(date.today()),
        "notes": ""
    })
    plant_id = plant_response.json()["id"]
    
    # Add multiple harvests
    harvests = [
        {"plant_id": plant_id, "harvest_date": str(date.today()), "quantity": 2.5, "unit": "lbs", "notes": "First harvest"},
        {"plant_id": plant_id, "harvest_date": str(date.today()), "quantity": 1.8, "unit": "lbs", "notes": "Second harvest"}
    ]
    
    for harvest in harvests:
        response = client.post(f"/api/garden/plants/{plant_id}/harvests", json=harvest)
        assert response.status_code == 200
    
    # List harvests
    response = client.get(f"/api/garden/plants/{plant_id}/harvests")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 2
    assert sum(h["quantity"] for h in data) == 4.3

def test_delete_harvest(client, test_db):
    """Test deleting a harvest record.
    
    Verifies:
    - Harvest can be deleted using its ID
    - Harvest is no longer returned in list after deletion
    """
    # Create bed and plant in FLOWERING state
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    plant_response = client.post("/api/garden/plants", json={
        "name": "Test Plant",
        "variety": "Test",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "FLOWERING",
        "quantity": 1,
        "expected_harvest_date": str(date.today()),
        "notes": ""
    })
    plant_id = plant_response.json()["id"]
    
    # Add a harvest
    harvest_data = {
        "plant_id": plant_id,
        "harvest_date": str(date.today()),
        "quantity": 2.5,
        "unit": "lbs",
        "notes": "Test harvest"
    }
    response = client.post(f"/api/garden/plants/{plant_id}/harvests", json=harvest_data)
    assert response.status_code == 200
    harvest_id = response.json()["id"]
    
    # Delete the harvest
    response = client.delete(f"/api/garden/plants/{plant_id}/harvests/{harvest_id}")
    assert response.status_code == 200
    
    # Verify harvest was deleted
    response = client.get(f"/api/garden/plants/{plant_id}/harvests")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

def test_invalid_harvest_quantity(client, test_db):
    """Test validation of harvest quantity.
    
    Verifies:
    - Harvest quantity must be greater than 0
    - Invalid quantities result in a 422 validation error
    """
    # Create bed and plant in FLOWERING state
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    plant_response = client.post("/api/garden/plants", json={
        "name": "Test Plant",
        "variety": "Test",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "FLOWERING",
        "quantity": 1,
        "expected_harvest_date": str(date.today()),
        "notes": ""
    })
    plant_id = plant_response.json()["id"]
    
    # Try to add harvest with invalid quantity
    harvest_data = {
        "plant_id": plant_id,
        "harvest_date": str(date.today()),
        "quantity": 0,  # Invalid - must be > 0
        "unit": "lbs",
        "notes": "Test harvest"
    }
    response = client.post(f"/api/garden/plants/{plant_id}/harvests", json=harvest_data)
    assert response.status_code == 422  # Validation error