"""Tests for plant management functionality."""
import pytest
from datetime import date

def test_create_plant(client, test_db):
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": "Test notes"
    })
    bed_id = bed_response.json()["id"]
    
    plant_data = {
        "name": "Tomato",
        "variety": "Cherry",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "season": "SUMMER",
        "expected_harvest_date": str(date.today()),
        "notes": "Test plant"
    }
    
    response = client.post("/api/garden/plants", json=plant_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Tomato"
    assert data["status"] == "PLANTED"

def test_invalid_plant_location(client, test_db):
    plant_data = {
        "name": "Tomato",
        "variety": "Cherry",
        "planting_date": str(date.today()),
        "location": "Bed 999",  # Non-existent bed
        "status": "PLANTED",
        "season": "SUMMER",
        "expected_harvest_date": str(date.today()),
        "notes": "Test plant"
    }
    
    response = client.post("/api/garden/plants", json=plant_data)
    assert response.status_code == 404

def test_plant_status_transition(client, test_db):
    # Create bed and plant
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    plant_response = client.post("/api/garden/plants", json={
        "name": "Tomato",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "season": "SUMMER",
        "notes": ""
    })
    plant_id = plant_response.json()["id"]
    
    # Test valid transition
    response = client.patch(f"/api/garden/plants/{plant_id}/status", json={"new_status": "SPROUTED"})
    assert response.status_code == 200
    assert response.json()["status"] == "SPROUTED"
    
    # Test invalid transition
    response = client.patch(f"/api/garden/plants/{plant_id}/status", json={"new_status": "FINISHED"})
    assert response.status_code == 400

def test_list_plants_by_season(client, test_db):
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    # Create plants for different seasons
    for season in ["SUMMER", "WINTER"]:
        client.post("/api/garden/plants", json={
            "name": f"{season} Plant",
            "variety": "Test",
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": "PLANTED",
            "season": season,
            "expected_harvest_date": str(date.today()),
            "notes": ""
        })
    
    response = client.get("/api/garden/plants?season=SUMMER")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "SUMMER Plant"

def test_plant_image_upload(client, test_db, mock_storage):
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
        "season": "SUMMER",
        "notes": ""
    })
    plant_id = plant_response.json()["id"]
    
    # Test image upload
    test_image = b"fake image content"
    files = {"file": ("test.jpg", test_image, "image/jpeg")}
    response = client.post(
        f"/api/images/plants/{plant_id}/upload",
        files=files
    )
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "taken_date" in data

def test_season_enum_validation(client, test_db):
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    response = client.post("/api/garden/plants", json={
        "name": "Test Plant",
        "variety": "Test",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "season": "INVALID_SEASON",
        "notes": ""
    })
    assert response.status_code == 422
    data = response.json()
    assert "season" in str(data["detail"])