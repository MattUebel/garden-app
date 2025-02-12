from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import pandas as pd
import plotly.express as px
import numpy as np
from sqlalchemy import distinct
from ..models import GardenStats, PlantStatus, DBPlant, DBGardenBed
from ..database import get_db

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("", response_model=GardenStats)
def get_garden_stats(db: Session = Depends(get_db)) -> GardenStats:
    all_plants = db.query(DBPlant).all()
    
    # Initialize counts for all statuses
    status_counts = {status.value: 0 for status in PlantStatus}
    total_plants = 0
    
    # Count plants
    for plant in all_plants:
        if plant.status in status_counts:
            status_counts[plant.status] += plant.quantity
        total_plants += plant.quantity
    
    return GardenStats(
        total_plants=total_plants,
        plants_by_status=status_counts
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
    total_space_used = 0
    plants_by_status = {status.value: 0 for status in PlantStatus}
    plants_by_year = {}
    
    # Count plants in this bed
    for plant in bed.plants:
        # If year filter is applied, only count plants from that year
        if year_int is not None and plant.year != year_int:
            continue
            
        total_plants += plant.quantity
        total_space_used += plant.quantity * plant.space_required
        plants_by_status[plant.status] += plant.quantity
        plants_by_year[plant.year] = plants_by_year.get(plant.year, 0) + plant.quantity
    
    # Calculate space utilization
    try:
        dimensions = bed.dimensions.split('x')
        total_bed_space = int(dimensions[0]) * int(dimensions[1])
        space_utilization = f"{(total_space_used / total_bed_space) * 100:.1f}%"
    except (IndexError, ValueError):
        space_utilization = "N/A"
    
    return {
        "bed_name": bed.name,
        "dimensions": bed.dimensions,
        "total_plants": total_plants,
        "total_space_used": total_space_used,
        "plants_by_status": plants_by_status,
        "plants_by_year": plants_by_year,
        "space_utilization": space_utilization
    }

@router.get("/charts/plants-by-season")
def get_plants_by_season_chart(db: Session = Depends(get_db)):
    # Initialize data for all seasons
    seasons_data = {season.value: 0 for season in Season}
    
    # Get plant counts
    plants = db.query(DBPlant).all()
    for plant in plants:
        if plant.season in seasons_data:
            seasons_data[plant.season] += 1
    
    # Create dataframe with all seasons
    df = pd.DataFrame([
        {"season": season, "count": count} 
        for season, count in seasons_data.items()
    ])
    
    fig = px.bar(
        df,
        x="season",
        y="count",
        title="Plants by Season",
        labels={"season": "Season", "count": "Number of Plants"}
    )
    
    # Ensure integer y-axis
    fig.update_yaxes(tickmode="linear", tick0=0, dtick=1)
    
    # Convert to dict and handle numpy types
    fig_dict = fig.to_dict()
    return JSONResponse(content=_convert_numpy(fig_dict))

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
    if isinstance(obj, (np.ndarray, np.generic)):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: _convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_numpy(i) for i in obj]
    return obj