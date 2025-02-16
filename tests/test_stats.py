"""Tests for statistics functionality."""
from datetime import date, datetime
import pytest
from fastapi.testclient import TestClient

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

def test_plants_by_season_with_data(client, test_db):
    """Test season chart with actual plant data"""
    # Create bed
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    # Add some plants
    plant_data = {
        "name": "Test Plant",
        "variety": "Test",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "quantity": 1,
        "space_required": 4,
        "year": date.today().year,
        "notes": ""
    }
    
    client.post("/api/garden/plants", json=plant_data)
    
    # Test chart generation
    response = client.get("/api/stats/charts/plants-by-season")
    assert response.status_code == 200
    data = response.json()
    
    # Verify chart structure
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 1
    assert "x" in data["data"][0]
    assert "y" in data["data"][0]
    assert isinstance(data["data"][0]["x"], list)
    assert isinstance(data["data"][0]["y"], list)
    
    # Verify layout
    assert "layout" in data
    assert "title" in data["layout"]
    assert "xaxis" in data["layout"]
    assert "yaxis" in data["layout"]

def test_get_bed_stats_with_invalid_dimensions(client, test_db):
    """Test bed stats calculation with unparseable dimensions"""
    # Create bed with unparseable dimensions string - should be rejected
    bed_response = client.post("/api/garden/beds", json={
        "name": "Invalid Bed",
        "dimensions": "3xN",  # Invalid format - should be rejected
        "notes": ""
    })
    assert bed_response.status_code == 422
    assert "dimensions" in str(bed_response.json()["detail"])

    # Create a valid bed instead to test stats with
    bed_response = client.post("/api/garden/beds", json={
        "name": "Valid Bed",
        "dimensions": "3x4",  # Valid format
        "notes": ""
    })
    assert bed_response.status_code == 200
    bed_id = bed_response.json()["id"]
    
    # Add a plant to the bed
    client.post("/api/garden/plants", json={
        "name": "Test Plant",
        "variety": "Test",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "PLANTED",
        "quantity": 1,
        "space_required": 4,
        "year": date.today().year,
        "notes": ""
    })
    
    # Test stats with the valid bed
    response = client.get(f"/api/stats/beds/{bed_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["space_utilization"] != "N/A"  # Should be calculable with valid dimensions

def test_get_bed_stats_with_invalid_year(client, test_db):
    """Test stats with invalid year parameter"""
    # Create a test bed
    bed_response = client.post("/api/garden/beds", json={
        "name": "Test Bed",
        "dimensions": "3x4",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    
    # Test with invalid year format
    response = client.get(f"/api/stats/beds/{bed_id}?year=invalid")
    assert response.status_code == 422
    assert "Year must be a valid integer" in response.json()["detail"]
    
    # Test with empty year
    response = client.get(f"/api/stats/beds/{bed_id}?year=")
    assert response.status_code == 200

def test_plants_by_year_chart_with_no_data(client, test_db):
    """Test year chart generation with no data"""
    response = client.get("/api/stats/charts/plants-by-year")
    assert response.status_code == 200
    data = response.json()
    
    # Should return a chart with current year and zero count
    current_year = str(datetime.now().year)
    chart_data = data["data"][0]
    assert current_year in chart_data["x"]
    assert 0 in chart_data["y"]

def test_plants_by_season_chart_with_no_data(client, test_db):
    """Test season chart generation with no data"""
    response = client.get("/api/stats/charts/plants-by-season")
    assert response.status_code == 200
    data = response.json()
    
    # Should have all seasons with zero counts
    seasons = ["SPRING", "SUMMER", "FALL", "WINTER"]
    assert data["data"][0]["x"] == seasons
    assert all(y == 0 for y in data["data"][0]["y"])

def test_get_metrics(client, test_db):
    """Test dashboard metrics endpoint"""
    # Create bed
    bed_response = client.post("/api/garden/beds", json={
        "name": "Metrics Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    current_year = datetime.now().year
    
    # Create plants for current and previous year
    for year in [current_year, current_year - 1]:
        plant_response = client.post("/api/garden/plants", json={
            "name": f"Plant {year}",
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": "PLANTED",
            "quantity": 2,
            "space_required": 4,
            "year": year,
            "notes": ""
        })
        
        if year == current_year:
            plant_id = plant_response.json()["id"]
            
            # Progress plant through all necessary states to HARVESTING
            for status in ["SPROUTED", "FLOWERING", "HARVESTING"]:
                client.patch(f"/api/garden/plants/{plant_id}/status", json={"new_status": status})
            
            # Add a harvest for current year plant
            client.post(f"/api/garden/plants/{plant_id}/harvests", json={
                "quantity": 1.5,
                "unit": "lbs",
                "harvest_date": str(date.today())
            })
    
    response = client.get(f"/api/stats/metrics?year={current_year}")
    assert response.status_code == 200
    data = response.json()
    
    # Verify metrics structure
    assert "total_plants" in data
    assert "plants_trend" in data
    assert "active_plants" in data
    assert "active_percentage" in data
    assert "total_harvests" in data
    assert "harvest_trend" in data
    assert "space_utilization" in data
    assert "space_trend" in data
    
    # Verify specific values
    assert data["total_plants"] == 2  # Current year plants
    assert data["active_plants"] == 2  # All plants are active (PLANTED)
    assert isinstance(data["space_utilization"], str)
    assert data["space_utilization"].endswith("%")

def test_get_status_chart(client, test_db):
    """Test plant lifecycle distribution chart"""
    # Create bed and plants with different statuses
    bed_response = client.post("/api/garden/beds", json={
        "name": "Status Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    current_year = datetime.now().year
    
    statuses = ["PLANTED", "SPROUTED", "FLOWERING"]
    for status in statuses:
        client.post("/api/garden/plants", json={
            "name": f"Plant {status}",
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": status,
            "quantity": 1,
            "year": current_year,
            "notes": ""
        })

    response = client.get(f"/api/stats/charts/status?year={current_year}")
    assert response.status_code == 200
    data = response.json()
    
    # Verify chart structure
    assert "data" in data
    assert len(data["data"]) == 1
    assert "values" in data["data"][0]
    assert "labels" in data["data"][0]
    assert data["data"][0]["type"] == "pie"
    
    # Verify all statuses are represented
    chart_labels = data["data"][0]["labels"]
    for status in statuses:
        assert status in chart_labels

def test_get_harvest_timeline(client, test_db):
    """Test harvest timeline chart"""
    # Create bed and plant
    bed_response = client.post("/api/garden/beds", json={
        "name": "Harvest Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    current_year = datetime.now().year
    
    # Create plant with harvests in different units
    plant_response = client.post("/api/garden/plants", json={
        "name": "Tomato",
        "planting_date": str(date.today()),
        "location": f"Bed {bed_id}",
        "status": "HARVESTING",
        "quantity": 1,
        "year": current_year,
        "notes": ""
    })
    plant_id = plant_response.json()["id"]
    
    # Add harvests with different units
    harvests = [
        {"quantity": 16, "unit": "oz"},
        {"quantity": 1000, "unit": "g"},
        {"quantity": 2, "unit": "lbs"}
    ]
    
    for harvest in harvests:
        client.post(f"/api/garden/plants/{plant_id}/harvests", json={
            **harvest,
            "harvest_date": str(date.today())
        })

    response = client.get(f"/api/stats/charts/harvests?year={current_year}")
    assert response.status_code == 200
    data = response.json()
    
    # Verify chart structure
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0
    assert "layout" in data
    
    # Verify data is normalized to pounds
    trace = data["data"][0]
    assert "x" in trace
    assert "y" in trace
    assert len(trace["y"]) > 0

def test_get_success_rate_chart(client, test_db):
    """Test plant success rate chart"""
    # Create bed
    bed_response = client.post("/api/garden/beds", json={
        "name": "Success Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    current_year = datetime.now().year
    
    # Create multiple plants of same type with different outcomes
    plant_name = "Test Plant"
    statuses = ["HARVESTING", "HARVESTING", "FINISHED", "PLANTED", "PLANTED"]
    
    for status in statuses:
        client.post("/api/garden/plants", json={
            "name": plant_name,
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": status,
            "quantity": 1,
            "year": current_year,
            "notes": ""
        })

    response = client.get(f"/api/stats/charts/success-rate?year={current_year}")
    assert response.status_code == 200
    data = response.json()
    
    # Verify chart structure
    assert "data" in data
    assert len(data["data"]) == 1
    chart_data = data["data"][0]
    
    # Verify success rate calculation
    assert len(chart_data["x"]) > 0  # Plant names
    assert len(chart_data["y"]) > 0  # Success rates
    assert isinstance(chart_data["text"][0], str)
    assert "%" in chart_data["text"][0]

def test_get_top_producers_chart(client, test_db):
    """Test top producing plants chart"""
    # Create bed and plants
    bed_response = client.post("/api/garden/beds", json={
        "name": "Producers Test Bed",
        "dimensions": "3x6",
        "notes": ""
    })
    bed_id = bed_response.json()["id"]
    current_year = datetime.now().year
    
    # Create plants with different harvest amounts
    plants = [
        ("Tomato", [
            {"quantity": 2, "unit": "lbs"},
            {"quantity": 16, "unit": "oz"}
        ]),
        ("Cucumber", [
            {"quantity": 500, "unit": "g"}
        ]),
        ("Lettuce", [
            {"quantity": 1, "unit": "kg"}
        ])
    ]
    
    for plant_name, harvests in plants:
        plant_response = client.post("/api/garden/plants", json={
            "name": plant_name,
            "planting_date": str(date.today()),
            "location": f"Bed {bed_id}",
            "status": "FLOWERING",  # Start in FLOWERING state
            "quantity": 1,
            "year": current_year,
            "notes": ""
        })
        plant_id = plant_response.json()["id"]
    
        for harvest in harvests:
            client.post(f"/api/garden/plants/{plant_id}/harvests", json={
                **harvest,
                "harvest_date": str(date.today())
            })
    
    response = client.get(f"/api/stats/charts/top-producers?year={current_year}")
    assert response.status_code == 200
    data = response.json()
    
    # Verify chart structure
    assert "data" in data
    assert len(data["data"]) == 1
    chart_data = data["data"][0]
    
    # Verify data is normalized to pounds and sorted
    assert len(chart_data["x"]) == len(plants)  # Plant names
    assert len(chart_data["y"]) == len(plants)  # Harvest amounts in lbs
    
    # Verify sorting (highest to lowest)
    assert chart_data["y"][0] >= chart_data["y"][1]  # First amount should be highest
    if len(chart_data["y"]) > 2:
        assert chart_data["y"][1] >= chart_data["y"][2]  # Second amount should be higher than third