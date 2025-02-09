import pytest
from datetime import date
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
from src.models import Season, PlantStatus


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_home_route(client):
    response = client.get("/api/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello"}


def test_about_route(client):
    response = client.get("/api/about")
    assert response.status_code == 200
    assert response.json() == {"message": "This is the about page."}


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

def test_create_plant(client, test_db):
    # Create a bed first
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
        "variety": "Cherry",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "season": "SUMMER",
        "expected_harvest_date": str(date.today()),
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
    # Create bed
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
    
    # Test filtering by season
    response = client.get("/api/garden/plants?season=SUMMER")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "SUMMER Plant"

def test_get_garden_stats(client, test_db):
    # Create bed
    bed_response = client.post("/api/garden/beds", json={
        "name": "Stats Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    # Create plants with different statuses and seasons
    test_data = [
        ("SUMMER", "PLANTED"),
        ("SUMMER", "SPROUTED"),
        ("WINTER", "PLANTED")
    ]
    
    for season, status in test_data:
        client.post("/api/garden/plants", json={
            "name": f"Test Plant",
            "variety": "Test",
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": status,
            "season": season,
            "expected_harvest_date": str(date.today()),
            "notes": ""
        })
    
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_plants"] == 3
    assert data["plants_by_status"]["PLANTED"] == 2
    assert data["plants_by_status"]["SPROUTED"] == 1
    assert data["plants_by_season"]["SUMMER"] == 2
    assert data["plants_by_season"]["WINTER"] == 1

def test_get_bed_stats(client, test_db):
    # Create bed
    bed_response = client.post("/api/garden/beds", json={
        "name": "Stats Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    # Add two plants to the bed
    for _ in range(2):
        client.post("/api/garden/plants", json={
            "name": "Test Plant",
            "variety": "Test",
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": "PLANTED",
            "season": "SUMMER",
            "expected_harvest_date": str(date.today()),
            "notes": ""
        })
    
    response = client.get(f"/api/stats/beds/{bed_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["bed_name"] == "Stats Test Bed"
    assert data["total_plants"] == 2
    assert data["plants_by_status"]["PLANTED"] == 2
    assert data["plants_by_season"]["SUMMER"] == 2
    assert "space_utilization" in data

def test_get_nonexistent_bed_stats(client, test_db):
    response = client.get("/api/stats/beds/999")
    assert response.status_code == 404

def test_plants_by_season_chart(client, test_db):
    # Create bed
    bed_response = client.post("/api/garden/beds", json={
        "name": "Chart Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    # Add plants for different seasons
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
    
    response = client.get("/api/stats/charts/plants-by-season")
    assert response.status_code == 200
    data = response.json()
    
    # Check if the response contains plotly chart data
    assert "data" in data
    assert "layout" in data

def test_create_garden_bed_invalid_dimensions(client, test_db):
    response = client.post("/api/garden/beds", json={
        "name": "Invalid Bed",
        "dimensions": "invalid",
        "notes": "Test notes"
    })
    assert response.status_code == 422
    data = response.json()
    assert "dimensions" in str(data["detail"])

def test_database_connection_error(client, monkeypatch):
    """Test that database connection errors are handled gracefully."""
    from sqlalchemy.orm import Session
    from src.database import get_db
    
    def mock_db():
        raise Exception("Database connection error")
    
    monkeypatch.setattr("src.database.get_db", mock_db)
    response = client.get("/api/garden/beds")
    assert response.status_code == 500
    assert "Database connection error" in response.text

def test_plant_image_upload(client, test_db):
    # Create bed and plant first
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

def test_plant_image_upload_invalid_plant(client, test_db):
    test_image = b"fake image content"
    files = {"file": ("test.jpg", test_image, "image/jpeg")}
    response = client.post("/api/images/plants/999/upload", files=files)
    assert response.status_code == 404
    assert response.json()["detail"] == "Plant not found"

def test_plant_dimension_validation(client, test_db):
    # Test various invalid dimension formats
    invalid_dimensions = ["0x0", "-1x5", "axb", "10", "10x", "x10"]
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    for dims in invalid_dimensions:
        response = client.post("/api/garden/beds", json={
            "name": "Invalid Bed",
            "dimensions": dims,
            "notes": ""
        })
        assert response.status_code == 422
        data = response.json()
        assert "dimensions" in str(data["detail"])

def test_malformed_json_handling(client):
    response = client.post(
        "/api/garden/beds",
        headers={"Content-Type": "application/json"},
        content="{invalid json"
    )
    assert response.status_code == 422
    data = response.json()
    assert "json" in str(data["detail"]).lower()

def test_season_enum_validation(client, test_db):
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    # Test invalid season
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

def test_concurrent_status_updates(client, test_db):
    # Create test bed and plant
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
    
    # Simulate concurrent updates
    responses = []
    for new_status in ["SPROUTED", "FLOWERING"]:
        response = client.patch(
            f"/api/garden/plants/{plant_id}/status",
            json={"new_status": new_status}
        )
        responses.append(response)
    
    # Check that one succeeded and maintains data integrity
    assert any(r.status_code == 200 for r in responses)
    
    # Verify final state
    response = client.get(f"/api/garden/plants/{plant_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["SPROUTED", "FLOWERING"]
