"""Tests for statistics functionality."""
from datetime import date, datetime

def test_get_garden_stats(client, test_db):
    # Create bed and test plants
    bed_response = client.post("/api/garden/beds", json={
        "name": "Stats Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    # Create plants with different statuses
    test_data = [
        ("PLANTED", 2),
        ("SPROUTED", 1)
    ]
    
    for status, quantity in test_data:
        client.post("/api/garden/plants", json={
            "name": f"Test Plant",
            "variety": "Test",
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": status,
            "quantity": quantity,
            "expected_harvest_date": str(date.today()),
            "notes": ""
        })
    
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_plants"] == 3
    assert data["plants_by_status"]["PLANTED"] == 2
    assert data["plants_by_status"]["SPROUTED"] == 1

def test_get_bed_stats(client, test_db):
    # Create bed and test plants
    bed_response = client.post("/api/garden/beds", json={
        "name": "Stats Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    # Create plants with different statuses
    test_data = [
        ("PLANTED", 2),
        ("SPROUTED", 1)
    ]
    
    for status, quantity in test_data:
        client.post("/api/garden/plants", json={
            "name": f"Test Plant",
            "variety": "Test",
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": status,
            "quantity": quantity,
            "expected_harvest_date": str(date.today()),
            "notes": ""
        })
    
    response = client.get(f"/api/stats/beds/{bed_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_plants"] == 3
    assert data["plants_by_status"]["PLANTED"] == 2
    assert data["plants_by_status"]["SPROUTED"] == 1
    assert "space_utilization" in data

def test_get_bed_stats_with_year_filter(client, test_db):
    # Create bed
    bed_response = client.post("/api/garden/beds", json={
        "name": "Stats Test Bed",
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
            "variety": "Test",
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": "PLANTED",
            "year": year,
            "expected_harvest_date": str(date.today()),
            "notes": ""
        })
    
    # Test current year filter
    response = client.get(f"/api/stats/beds/{bed_id}?year={current_year}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_plants"] == 1
    
    # Test previous year filter
    response = client.get(f"/api/stats/beds/{bed_id}?year={current_year - 1}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_plants"] == 1

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

def test_get_available_years(client, test_db):
    # Create bed
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
            "year": year,
            "expected_harvest_date": str(date.today()),
            "notes": ""
        })
    
    response = client.get("/api/stats/years")
    assert response.status_code == 200
    data = response.json()
    
    # Should include all years with plants plus next year
    assert current_year - 1 in data
    assert current_year in data
    assert current_year + 1 in data
    assert len(data) == 3  # Previous, current, and next year
    assert data == sorted(data, reverse=True)  # Should be sorted newest first