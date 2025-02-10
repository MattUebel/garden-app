"""Tests for garden statistics functionality."""
import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient

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
    """Test that stats are updated correctly after deleting plants."""
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
        "quantity": 2,
        "notes": ""
    })
    plant_id = plant_response.json()["id"]
    
    # Verify initial stats
    stats_response = client.get("/api/stats")
    initial_stats = stats_response.json()
    assert initial_stats["total_plants"] == 2
    
    # Delete plant
    delete_response = client.delete(f"/api/garden/plants/{plant_id}")
    assert delete_response.status_code == 200
    
    # Check updated stats
    updated_stats_response = client.get("/api/stats")
    updated_stats = updated_stats_response.json()
    assert updated_stats["total_plants"] == 0

def test_bed_stats_dimensions_utilization(client, test_db):
    """Test bed stats calculation with different bed dimensions and plant quantities."""
    # Create a bed with known dimensions
    bed_response = client.post("/api/garden/beds", json={
        "name": "Big Bed",
        "dimensions": "4x8",  # 32 square units
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    # Add plants that should take up different amounts of space
    plants_data = [
        {
            "name": "Tomato",
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": "PLANTED",
            "season": "SUMMER",
            "quantity": 4,  # Tomatoes typically need 4 square units each
            "notes": ""
        },
        {
            "name": "Lettuce",
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": "PLANTED",
            "season": "SPRING",
            "quantity": 8,  # Lettuce typically needs 1 square unit each
            "notes": ""
        }
    ]
    
    for plant_data in plants_data:
        response = client.post("/api/garden/plants", json=plant_data)
        assert response.status_code == 200
    
    # Check bed stats
    response = client.get(f"/api/stats/beds/{bed_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_plants"] == 12  # Total number of plants
    assert "space_utilization" in data

def test_plants_by_season_chart_data(client, test_db):
    """Test the season chart data structure with plants in different seasons."""
    # Create a bed
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    # Add plants in different seasons
    seasons = ["SPRING", "SUMMER", "FALL", "WINTER"]
    for i, season in enumerate(seasons, 1):
        response = client.post("/api/garden/plants", json={
            "name": f"Plant {i}",
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": "PLANTED",
            "season": season,
            "quantity": i,  # Different quantities
            "notes": ""
        })
        assert response.status_code == 200
    
    # Check season chart
    response = client.get("/api/stats/charts/plants-by-season")
    assert response.status_code == 200
    data = response.json()
    
    # Verify chart data structure
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0
    assert "layout" in data

def test_garden_stats_with_all_plant_statuses(client, test_db):
    """Test garden stats with plants in every possible status."""
    # Create a bed
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    # Add plants and progress them through all statuses
    statuses = ["PLANTED", "SPROUTED", "FLOWERING", "HARVESTING", "FINISHED"]
    for i, status in enumerate(statuses, 1):
        # Create plant
        plant_response = client.post("/api/garden/plants", json={
            "name": f"Plant {i}",
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": "PLANTED",
            "season": "SUMMER",
            "quantity": 1,
            "notes": ""
        })
        plant_id = plant_response.json()["id"]
        
        # Progress to target status
        for target_status in statuses[:statuses.index(status) + 1]:
            if target_status != "PLANTED":
                status_response = client.patch(f"/api/garden/plants/{plant_id}/status", 
                    json={"new_status": target_status})
                assert status_response.status_code == 200
    
    # Check garden stats
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    
    # Verify we have plants in each status
    for status in statuses:
        assert data["plants_by_status"][status] > 0

def test_bed_stats_nonexistent_bed(client, test_db):
    """Test stats for a nonexistent bed."""
    response = client.get("/api/stats/beds/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_bed_stats_by_year(client, test_db):
    """Test bed statistics filtering by year"""
    bed_response = client.post("/api/garden/beds", json={
        "name": "Stats Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    current_year = datetime.now().year
    
    # Create plants for different years
    for year in [current_year - 1, current_year]:
        client.post("/api/garden/plants", json={
            "name": f"Plant {year}",
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": "PLANTED",
            "season": "SUMMER",
            "year": year,
            "quantity": 2,
            "notes": ""
        })
    
    # Test current year stats
    response = client.get(f"/api/stats/beds/{bed_id}?year={current_year}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_plants"] == 2
    assert data["plants_by_year"][str(current_year)] == 2
    
    # Test previous year stats
    response = client.get(f"/api/stats/beds/{bed_id}?year={current_year - 1}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_plants"] == 2
    assert data["plants_by_year"][str(current_year - 1)] == 2
    
    # Test all years (no year filter)
    response = client.get(f"/api/stats/beds/{bed_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_plants"] == 4
    assert data["plants_by_year"][str(current_year)] == 2
    assert data["plants_by_year"][str(current_year - 1)] == 2

def test_bed_stats_year_comparison(client, test_db):
    """Test the year-over-year comparison in bed statistics"""
    bed_response = client.post("/api/garden/beds", json={
        "name": "Stats Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    current_year = datetime.now().year
    
    # Create plants across multiple years with different quantities
    year_quantities = {
        current_year - 2: 1,
        current_year - 1: 3,
        current_year: 2
    }
    
    for year, quantity in year_quantities.items():
        client.post("/api/garden/plants", json={
            "name": f"Plant {year}",
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": "PLANTED",
            "season": "SUMMER",
            "year": year,
            "quantity": quantity,
            "notes": ""
        })
    
    # Test year comparison data
    response = client.get(f"/api/stats/beds/{bed_id}")
    assert response.status_code == 200
    data = response.json()
    
    # Verify year-specific plant counts
    for year, expected_quantity in year_quantities.items():
        assert data["plants_by_year"][str(year)] == expected_quantity
    
    # Verify total matches sum of all years
    assert data["total_plants"] == sum(year_quantities.values())

def test_get_available_years(client, test_db):
    """Test retrieving available years for plants"""
    # Create bed
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    current_year = datetime.now().year
    
    # Create plants for different years
    years = [current_year - 2, current_year - 1, current_year]
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
    
    # Test years endpoint
    response = client.get("/api/stats/years")
    assert response.status_code == 200
    available_years = response.json()
    
    # Should include all years with plants plus next year, sorted in descending order
    expected_years = sorted(years + [current_year + 1], reverse=True)
    assert available_years == expected_years
    
    # Test with no plants
    client.delete(f"/api/garden/beds/{bed_id}")
    response = client.get("/api/stats/years")
    assert response.status_code == 200
    available_years = response.json()
    
    # Should include only current and next year when no plants exist, sorted in descending order
    assert available_years == sorted([current_year, current_year + 1], reverse=True)