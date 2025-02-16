from datetime import datetime
from typing import Dict, List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import distinct, func
from fastapi.responses import JSONResponse
import pandas as pd
import plotly.express as px
import numpy as np
from ..models import GardenStats, PlantStatus, DBPlant, DBGardenBed, DBHarvest
from ..database import get_db

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("", response_model=GardenStats)
def get_garden_stats(db: Session = Depends(get_db)) -> GardenStats:
    all_plants = db.query(DBPlant).all()
    
    # Initialize counts for all statuses
    status_counts = {status.value: 0 for status in PlantStatus}
    season_counts = {"SPRING": 0, "SUMMER": 0, "FALL": 0, "WINTER": 0}
    total_plants = 0
    plants_by_year = {}
    
    # Count plants
    for plant in all_plants:
        if plant.status in status_counts:
            status_counts[plant.status] += plant.quantity
        total_plants += plant.quantity
        plants_by_year[str(plant.year)] = plants_by_year.get(str(plant.year), 0) + plant.quantity
    
    return GardenStats(
        total_plants=total_plants,
        plants_by_status=status_counts,
        plants_by_season=season_counts,
        plants_by_year=plants_by_year
    )

@router.get("/beds/{bed_id}")
def get_bed_stats(
    bed_id: int,
    year: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    """Get statistics for a specific garden bed."""
    bed = db.query(DBGardenBed).filter(DBGardenBed.id == bed_id).first()
    if not bed:
        raise HTTPException(status_code=404, detail="Garden bed not found")
    
    # Convert year to int if provided
    year_int = None
    if year and year.strip():
        try:
            year_int = int(year)
        except ValueError:
            raise HTTPException(status_code=422, detail="Year must be a valid integer")
    
    # Initialize counts
    total_plants = 0
    total_space_used = 0  # in square inches
    plants_by_status = {status.value: 0 for status in PlantStatus}
    plants_by_season = {"SPRING": 0, "SUMMER": 0, "FALL": 0, "WINTER": 0}
    plants_by_year = {}
    
    # Count plants in this bed
    for plant in bed.plants:
        # If year filter is applied, only count plants from that year
        if year_int is not None and plant.year != year_int:
            continue
            
        total_plants += plant.quantity
        total_space_used += plant.quantity * plant.space_required
        plants_by_status[plant.status] += plant.quantity
        plants_by_year[str(plant.year)] = plants_by_year.get(str(plant.year), 0) + plant.quantity
    
    # Calculate space utilization
    try:
        dimensions = bed.dimensions.split('x')
        # Convert bed dimensions from feet to square inches
        width_inches = int(dimensions[0]) * 12  # Convert feet to inches
        length_inches = int(dimensions[1]) * 12  # Convert feet to inches
        total_bed_space = width_inches * length_inches  # Total square inches
        space_utilization = f"{(total_space_used / total_bed_space) * 100:.1f}%"
    except (IndexError, ValueError):
        space_utilization = "N/A"
    
    return {
        "bed_name": bed.name,
        "dimensions": bed.dimensions,
        "total_plants": total_plants,
        "total_space_used": total_space_used,  # Just return the number
        "space_utilization": space_utilization,
        "plants_by_status": plants_by_status,
        "plants_by_season": plants_by_season,
        "plants_by_year": plants_by_year
    }

@router.get("/charts/plants-by-year")
def get_plants_by_year_chart(db: Session = Depends(get_db)):
    """Get a chart showing plant distribution by year"""
    plants = db.query(DBPlant).all()
    
    # Count plants by year
    year_counts = {}
    for plant in plants:
        if plant.year:
            year_counts[str(plant.year)] = year_counts.get(str(plant.year), 0) + plant.quantity
    
    # Create dataframe
    df = pd.DataFrame([
        {"year": year, "count": count} 
        for year, count in year_counts.items()
    ])
    
    if df.empty:
        current_year = str(datetime.now().year)
        df = pd.DataFrame([{"year": current_year, "count": 0}])
    
    # Create chart data directly instead of using plotly
    chart_data = {
        "data": [
            {
                "x": df["year"].tolist(),
                "y": df["count"].tolist(),
                "type": "bar",
                "name": "Plants"
            }
        ],
        "layout": {
            "title": "Plants by Year",
            "xaxis": {"title": "Year"},
            "yaxis": {
                "title": "Number of Plants",
                "tickmode": "linear",
                "tick0": 0,
                "dtick": 1
            }
        }
    }
    
    return JSONResponse(content=chart_data)

@router.get("/charts/plants-by-season")
def get_plants_by_season_chart(db: Session = Depends(get_db)):
    """Get a chart showing plant distribution by season."""
    plants = db.query(DBPlant).all()
    
    # Initialize counts for all seasons
    season_counts = {"SPRING": 0, "SUMMER": 0, "FALL": 0, "WINTER": 0}
    
    # Create dataframe for the chart
    df = pd.DataFrame([
        {"season": season, "count": count}
        for season, count in season_counts.items()
    ])
    
    # Create chart data directly
    chart_data = {
        "data": [{
            "x": df["season"].tolist(),
            "y": df["count"].tolist(),
            "type": "bar",
            "name": "Plants"
        }],
        "layout": {
            "title": "Plants by Season",
            "xaxis": {"title": "Season"},
            "yaxis": {
                "title": "Number of Plants",
                "tickmode": "linear",
                "tick0": 0,
                "dtick": 1
            }
        }
    }
    
    return chart_data

@router.get("/years")
def get_available_years(db: Session = Depends(get_db)):
    """Get list of years that have plants, plus current and next year"""
    current_year = datetime.now().year
    
    # First check if there are any garden beds at all
    if not db.query(DBGardenBed).first():
        return sorted([current_year, current_year + 1], reverse=True)
    
    # Get years from plants that belong to existing beds
    years = db.query(distinct(DBPlant.year)).\
        join(DBGardenBed).\
        filter(DBPlant.bed_id == DBGardenBed.id).\
        filter(DBPlant.year.isnot(None)).\
        all()
    # Convert from list of tuples to list of integers, excluding None values
    plant_years = [year[0] for year in years if year[0] is not None]
    
    # Always include current and next year
    result = set([current_year, current_year + 1])
    if plant_years:
        result.update(plant_years)
    
    return sorted(result, reverse=True)

def _convert_numpy(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, dict):
        return {k: _convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_numpy(x) for x in obj]
    elif isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    return obj

@router.get("/metrics")
def get_metrics(year: int = Query(default=None), db: Session = Depends(get_db)):
    """Get key metrics for the dashboard."""
    current_year = datetime.now().year
    year = year or current_year
    
    # Get current year stats
    curr_plants = db.query(DBPlant).filter(DBPlant.year == year).all()
    curr_total = sum(p.quantity for p in curr_plants)
    
    # Get previous year stats for trends
    prev_plants = db.query(DBPlant).filter(DBPlant.year == year - 1).all()
    prev_total = sum(p.quantity for p in prev_plants)
    
    # Calculate active plants (not FINISHED)
    active_plants = sum(p.quantity for p in curr_plants if p.status != PlantStatus.FINISHED.value)
    
    # Get harvest stats with proper joins and filters, handle harvest_date
    curr_harvests = (
        db.query(DBHarvest)
        .join(DBPlant)
        .filter(DBPlant.year == year)
        .filter(DBHarvest.harvest_date.isnot(None))
        .all()
    )
    curr_harvests_count = len(curr_harvests)
    
    prev_harvests = (
        db.query(DBHarvest)
        .join(DBPlant)
        .filter(DBPlant.year == year - 1)
        .filter(DBHarvest.harvest_date.isnot(None))
        .all()
    )
    prev_harvests_count = len(prev_harvests)

    # Calculate trends
    plants_trend = ((curr_total - prev_total) / prev_total * 100) if prev_total else 0
    harvest_trend = ((curr_harvests_count - prev_harvests_count) / prev_harvests_count * 100) if prev_harvests_count else 0
    
    # Calculate space utilization
    curr_beds = (db.query(DBGardenBed)
                 .join(DBPlant)
                 .filter(DBPlant.year == year)
                 .distinct()
                 .all())
    prev_beds = (db.query(DBGardenBed)
                 .join(DBPlant)
                 .filter(DBPlant.year == year - 1)
                 .distinct()
                 .all())
    
    def calculate_space_usage(plants, beds):
        total_space = sum(
            int(bed.dimensions.split('x')[0]) * int(bed.dimensions.split('x')[1])
            for bed in beds
        ) if beds else 0
        used_space = sum(p.space_required * p.quantity for p in plants if p.space_required)
        return used_space, total_space
    
    curr_used, curr_total_space = calculate_space_usage(curr_plants, curr_beds)
    prev_used, prev_total_space = calculate_space_usage(prev_plants, prev_beds)
    
    # Calculate trends
    plants_trend = ((curr_total - prev_total) / prev_total * 100) if prev_total else 0
    harvest_trend = ((curr_harvests_count - prev_harvests_count) / prev_harvests_count * 100) if prev_harvests_count else 0
    curr_util = (curr_used / curr_total_space * 100) if curr_total_space else 0
    prev_util = (prev_used / prev_total_space * 100) if prev_total_space else 0
    space_trend = curr_util - prev_util if prev_total_space else 0
    
    return {
        "total_plants": curr_total,
        "plants_trend": round(plants_trend, 1),
        "active_plants": active_plants,
        "active_percentage": round((active_plants / curr_total * 100) if curr_total else 0),
        "total_harvests": curr_harvests_count,
        "harvest_trend": round(harvest_trend, 1),
        "space_utilization": f"{round(curr_util)}%",
        "space_trend": round(space_trend, 1)
    }

@router.get("/charts/status")
def get_status_chart(year: int = Query(default=None), db: Session = Depends(get_db)):
    """Get plant lifecycle distribution chart data."""
    year = year or datetime.now().year
    
    # Count plants by status
    plants = db.query(DBPlant).filter(DBPlant.year == year).all()
    status_counts = {status.value: 0 for status in PlantStatus}
    
    for plant in plants:
        if plant.status in status_counts:
            status_counts[plant.status] += plant.quantity
    
    # Filter out statuses with 0 plants
    status_data = {k: v for k, v in status_counts.items() if v > 0}
    
    chart_data = {
        "data": [{
            "values": list(status_data.values()),
            "labels": list(status_data.keys()),
            "type": "pie",
            "hole": 0.4,
            "marker": {
                "colors": [
                    "#198754",  # PLANTED - success
                    "#0dcaf0",  # SPROUTED - info
                    "#ffc107",  # FLOWERING - warning
                    "#0d6efd",  # HARVESTING - primary
                    "#6c757d"   # FINISHED - secondary
                ]
            }
        }],
        "layout": {
            "showlegend": True,
            "legend": {"orientation": "h", "y": -0.2},
            "margin": {"t": 20, "b": 0, "l": 0, "r": 0}
        }
    }
    
    return chart_data

@router.get("/charts/harvests")
def get_harvest_timeline(year: int = Query(default=None), db: Session = Depends(get_db)):
    """Get harvest timeline chart data."""
    year = year or datetime.now().year
    
    # Get all harvests for the year with plant info
    harvests = db.query(
        DBHarvest, 
        DBPlant.name.label('plant_name')
    ).join(DBPlant).filter(
        DBPlant.year == year
    ).all()
    
    # Create timeline data
    timeline_data = {}
    for harvest, plant_name in harvests:
        month = harvest.harvest_date.strftime('%Y-%m')
        timeline_data.setdefault(month, {})
        
        # Normalize all harvests to pounds for consistency
        quantity = harvest.quantity
        if harvest.unit == 'oz':
            quantity = quantity / 16
        elif harvest.unit == 'g':
            quantity = quantity / 453.592
        elif harvest.unit == 'kg':
            quantity = quantity * 2.20462
        
        timeline_data[month][plant_name] = timeline_data[month].get(plant_name, 0) + quantity
    
    # Convert to plotly format
    months = sorted(timeline_data.keys())
    plants = sorted(set(plant for month_data in timeline_data.values() for plant in month_data.keys()))
    
    # If no data, create empty chart with current month
    if not months:
        current_month = datetime.now().strftime('%Y-%m')
        months = [current_month]
        plants = []
    
    traces = []
    for plant in plants:
        trace = {
            "x": months,
            "y": [timeline_data.get(month, {}).get(plant, 0) for month in months],
            "name": plant,
            "type": "scatter",
            "mode": "lines+markers"
        }
        traces.append(trace)
    
    # Always return at least one trace for empty data
    if not traces:
        traces = [{
            "x": months,
            "y": [0] * len(months),
            "name": "No harvests",
            "type": "scatter",
            "mode": "lines+markers"
        }]
    
    chart_data = {
        "data": traces,
        "layout": {
            "title": "Monthly Harvest Quantities (in lbs)",
            "xaxis": {"title": "Month"},
            "yaxis": {"title": "Pounds Harvested"},
            "hovermode": "x unified",
            "showlegend": True,
            "legend": {"orientation": "h", "y": -0.2}
        }
    }
    
    return chart_data

@router.get("/charts/success-rate")
def get_success_rate_chart(year: int = Query(default=None), db: Session = Depends(get_db)):
    """Get plant success rate chart data."""
    year = year or datetime.now().year
    
    # Get all plants for the year
    plants = db.query(DBPlant).filter(DBPlant.year == year).all()
    
    # Group plants by name
    plant_stats = {}
    for plant in plants:
        if plant.name not in plant_stats:
            plant_stats[plant.name] = {"total": 0, "success": 0}
        
        plant_stats[plant.name]["total"] += plant.quantity
        if plant.status in [PlantStatus.HARVESTING.value, PlantStatus.FINISHED.value]:
            plant_stats[plant.name]["success"] += plant.quantity
    
    # Calculate success rates
    success_rates = [
        {
            "name": name,
            "rate": (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0,
            "total": stats["total"]
        }
        for name, stats in plant_stats.items()
        if stats["total"] >= 5  # Only show plants with meaningful sample size
    ]
    
    # Sort by success rate
    success_rates.sort(key=lambda x: x["rate"], reverse=True)
    
    chart_data = {
        "data": [{
            "x": [item["name"] for item in success_rates],
            "y": [item["rate"] for item in success_rates],
            "type": "bar",
            "text": [f"{item['rate']:.1f}%<br>({item['total']} plants)" for item in success_rates],
            "textposition": "auto",
            "marker": {
                "color": [
                    "success" if rate["rate"] >= 80 else
                    "warning" if rate["rate"] >= 60 else
                    "danger"
                    for rate in success_rates
                ]
            }
        }],
        "layout": {
            "title": "Growth Success Rate by Plant Type",
            "xaxis": {"title": "Plant Type"},
            "yaxis": {
                "title": "Success Rate (%)",
                "range": [0, 100]
            },
            "margin": {"b": 100},
            "showlegend": False
        }
    }
    
    return chart_data

@router.get("/charts/top-producers")
def get_top_producers_chart(year: int = Query(default=None), db: Session = Depends(get_db)):
    """Get chart data for top producing plants."""
    year = year or datetime.now().year

    def convert_to_lbs(quantity: float, unit: str) -> float:
        conversions = {
            "lbs": 1,
            "oz": 1/16,
            "g": 0.00220462,
            "kg": 2.20462
        }
        return quantity * conversions.get(unit, 1)

    # Get all plants with harvests for the year with eager loading
    plants = (db.query(DBPlant)
            .options(joinedload(DBPlant.harvests))
            .filter(DBPlant.year == year)
            .all())

    # Group and sum harvests by plant name
    plant_totals = {}
    
    # First collect all plant names, even those without harvests
    for plant in plants:
        if plant.name not in plant_totals:
            plant_totals[plant.name] = 0
        
        # Add up harvests if any exist
        if plant.harvests:
            plant_totals[plant.name] += sum(
                convert_to_lbs(h.quantity, h.unit) 
                for h in plant.harvests
            )

    if not plant_totals:
        return {
            "data": [{
                "x": ["No harvests"],
                "y": [0],
                "type": "bar",
                "text": ["0 lbs"],
                "textposition": "auto"
            }]
        }

    # Sort by total weight and format for chart
    sorted_plants = sorted(plant_totals.items(), key=lambda x: x[1], reverse=True)
    plant_names = [plant[0] for plant in sorted_plants]
    plant_weights = [plant[1] for plant in sorted_plants]

    return {
        "data": [{
            "x": plant_names,
            "y": plant_weights,
            "type": "bar",
            "text": [f"{weight:.2f} lbs" for weight in plant_weights],
            "textposition": "auto"
        }]
    }