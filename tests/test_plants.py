"""Tests for plant management functionality."""
import pytest
from datetime import date, datetime

def test_create_plant(client, test_db):
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": "Test notes"
    })
    bed_id = bed_response.json()["id"]
    current_year = datetime.now().year
    
    plant_data = {
        "name": "Tomato",
        "variety": "Cherry",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "season": "SUMMER",
        "year": current_year,
        "quantity": 1,
        "expected_harvest_date": str(date.today()),
        "notes": "Test plant"
    }
    
    response = client.post("/api/garden/plants", json=plant_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Tomato"
    assert data["status"] == "PLANTED"
    assert data["year"] == current_year
    assert data["quantity"] == 1

def test_invalid_plant_location(client, test_db):
    current_year = datetime.now().year
    plant_data = {
        "name": "Tomato",
        "variety": "Cherry",
        "planting_date": str(date.today()),
        "location": "Bed 999",  # Non-existent bed
        "status": "PLANTED",
        "season": "SUMMER",
        "year": current_year,
        "quantity": 1,
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
    current_year = datetime.now().year
    
    plant_response = client.post("/api/garden/plants", json={
        "name": "Tomato",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "season": "SUMMER",
        "year": current_year,
        "quantity": 1,
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
    current_year = datetime.now().year
    
    # Create plants for different seasons
    for season in ["SUMMER", "WINTER"]:
        client.post("/api/garden/plants", json={
            "name": f"{season} Plant",
            "variety": "Test",
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": "PLANTED",
            "season": season,
            "year": current_year,
            "quantity": 1,
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
    current_year = datetime.now().year
    
    plant_response = client.post("/api/garden/plants", json={
        "name": "Test Plant",
        "variety": "Test",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "season": "SUMMER",
        "year": current_year,
        "quantity": 1,
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
    current_year = datetime.now().year
    
    response = client.post("/api/garden/plants", json={
        "name": "Test Plant",
        "variety": "Test",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "season": "INVALID_SEASON",
        "year": current_year,
        "quantity": 1,
        "notes": ""
    })
    assert response.status_code == 422
    data = response.json()
    assert "season" in str(data["detail"])

def test_create_plant_with_year(client, test_db):
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": "Test notes"
    })
    bed_id = bed_response.json()["id"]
    current_year = datetime.now().year
    
    plant_data = {
        "name": "Tomato",
        "variety": "Cherry",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "season": "SUMMER",
        "year": current_year,
        "expected_harvest_date": str(date.today()),
        "notes": "Test plant"
    }
    
    response = client.post("/api/garden/plants", json=plant_data)
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == current_year

def test_create_plant_without_year(client, test_db):
    """Test that year defaults to current year when not provided"""
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": "Test notes"
    })
    bed_id = bed_response.json()["id"]
    current_year = datetime.now().year
    
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
    assert data["year"] == current_year

def test_invalid_year_validation(client, test_db):
    """Test that invalid years are rejected"""
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": "Test notes"
    })
    bed_id = bed_response.json()["id"]
    current_year = datetime.now().year
    
    # Test year too low
    plant_data = {
        "name": "Tomato",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "season": "SUMMER",
        "year": 1999,  # Below minimum
        "notes": "Test plant"
    }
    response = client.post("/api/garden/plants", json=plant_data)
    assert response.status_code == 422
    
    # Test year too high
    plant_data["year"] = current_year + 2  # Above maximum
    response = client.post("/api/garden/plants", json=plant_data)
    assert response.status_code == 422

def test_list_plants_by_year(client, test_db):
    """Test filtering plants by year"""
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    current_year = datetime.now().year
    
    # Create plants for different years
    years = [current_year - 1, current_year]
    for year in years:
        client.post("/api/garden/plants", json={
            "name": f"Plant {year}",
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": "PLANTED",
            "season": "SUMMER",
            "year": year,
            "notes": ""
        })
    
    # Test filtering by current year
    response = client.get(f"/api/garden/plants?year={current_year}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == f"Plant {current_year}"
    
    # Test filtering by previous year
    response = client.get(f"/api/garden/plants?year={current_year - 1}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == f"Plant {current_year - 1}"

def test_create_plant_with_space_required(client, test_db):
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": "Test notes"
    })
    bed_id = bed_response.json()["id"]
    current_year = datetime.now().year
    
    plant_data = {
        "name": "Tomato",
        "variety": "Cherry",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "season": "SUMMER",
        "year": current_year,
        "space_required": 8,
        "expected_harvest_date": str(date.today()),
        "notes": "Test plant"
    }
    
    response = client.post("/api/garden/plants", json=plant_data)
    assert response.status_code == 200
    data = response.json()
    assert data["space_required"] == 8

def test_update_plant_space_required(client, test_db):
    # First create a plant
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
        "year": datetime.now().year,
        "space_required": 4,
        "notes": "Test plant"
    }
    
    create_response = client.post("/api/garden/plants", json=plant_data)
    plant_id = create_response.json()["id"]
    
    # Update the space required
    update_data = create_response.json()
    update_data["space_required"] = 16
    
    update_response = client.patch(f"/api/garden/plants/{plant_id}", json=update_data)
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["space_required"] == 16