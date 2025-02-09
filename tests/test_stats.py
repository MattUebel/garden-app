"""Tests for statistics and analytics functionality."""
import pytest
from datetime import date

def test_get_garden_stats(client, test_db):
    # Create bed and test plants
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
    # Create bed and test data
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
    
def test_empty_stats(client, test_db):
    """Test stats endpoints with no data."""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_plants"] == 0
    assert all(count == 0 for count in data["plants_by_status"].values())
    assert all(count == 0 for count in data["plants_by_season"].values())

def test_stats_after_plant_deletion(client, test_db):
    """Test stats are updated after deleting plants."""
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
    
    # Check initial stats
    response = client.get("/api/stats")
    assert response.json()["total_plants"] == 1
    
    # Delete plant
    response = client.delete(f"/api/garden/plants/{plant_id}")
    assert response.status_code == 200
    
    # Check stats are updated
    response = client.get("/api/stats")
    data = response.json()
    assert data["total_plants"] == 0
    assert data["plants_by_status"]["PLANTED"] == 0
    assert data["plants_by_season"]["SUMMER"] == 0