from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import pandas as pd
import plotly.express as px
import numpy as np
from ..models import GardenStats, PlantStatus, Season, DBPlant, DBGardenBed
from ..database import get_db

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("", response_model=GardenStats)
def get_garden_stats(db: Session = Depends(get_db)) -> GardenStats:
    all_plants = db.query(DBPlant).all()
    
    # Initialize counts for all statuses and seasons
    status_counts = {status.value: 0 for status in PlantStatus}
    season_counts = {season.value: 0 for season in Season}
    total_plants = 0
    
    # Count plants
    for plant in all_plants:
        if plant.status in status_counts:
            status_counts[plant.status] += plant.quantity
        if plant.season in season_counts:
            season_counts[plant.season] += plant.quantity
        total_plants += plant.quantity
    
    return GardenStats(
        total_plants=total_plants,
        plants_by_status=status_counts,
        plants_by_season=season_counts
    )

@router.get("/beds/{bed_id}")
def get_bed_stats(
    bed_id: int,
    year: int | None = None,
    db: Session = Depends(get_db)
):
    """Get statistics for a specific garden bed."""
    bed = db.query(DBGardenBed).filter(DBGardenBed.id == bed_id).first()
    if not bed:
        raise HTTPException(status_code=404, detail="Garden bed not found")

    # Initialize counts
    total_plants = 0
    plants_by_status = {status.value: 0 for status in PlantStatus}
    plants_by_season = {season.value: 0 for season in Season}
    plants_by_year = {}

    # Count plants in this bed
    for plant in bed.plants:
        # If year filter is applied, only count plants from that year
        if year is not None and plant.year != year:
            continue
            
        total_plants += plant.quantity
        plants_by_status[plant.status] += plant.quantity
        plants_by_season[plant.season] += plant.quantity
        plants_by_year[plant.year] = plants_by_year.get(plant.year, 0) + plant.quantity

    # Calculate space utilization
    try:
        dimensions = bed.dimensions.split('x')
        total_space = int(dimensions[0]) * int(dimensions[1])
        space_utilization = f"{(total_plants / total_space) * 100:.1f}%"
    except (IndexError, ValueError):
        space_utilization = "N/A"

    return {
        "bed_name": bed.name,
        "dimensions": bed.dimensions,
        "total_plants": total_plants,
        "plants_by_status": plants_by_status,
        "plants_by_season": plants_by_season,
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

def _convert_numpy(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, (np.ndarray, np.generic)):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: _convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_numpy(i) for i in obj]
    return obj