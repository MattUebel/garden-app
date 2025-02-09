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
    
    # Count plants
    for plant in all_plants:
        if plant.status in status_counts:
            status_counts[plant.status] += 1
        if plant.season in season_counts:
            season_counts[plant.season] += 1
    
    return GardenStats(
        total_plants=len(all_plants),
        plants_by_status=status_counts,
        plants_by_season=season_counts
    )

@router.get("/beds/{bed_id}")
def get_bed_stats(bed_id: int, db: Session = Depends(get_db)):
    bed = db.query(DBGardenBed).filter(DBGardenBed.id == bed_id).first()
    if not bed:
        raise HTTPException(status_code=404, detail="Garden bed not found")
        
    bed_plants = db.query(DBPlant).filter(DBPlant.bed_id == bed_id).all()
    
    # Initialize counts for all statuses and seasons
    status_counts = {status.value: 0 for status in PlantStatus}
    season_counts = {season.value: 0 for season in Season}
    
    # Count plants
    for plant in bed_plants:
        if plant.status in status_counts:
            status_counts[plant.status] += 1
        if plant.season in season_counts:
            season_counts[plant.season] += 1
        
    # Calculate space utilization
    dimensions = bed.dimensions.split('x')
    try:
        area = float(dimensions[0]) * float(dimensions[1])
        utilization = f"{len(bed_plants)} plants in {area} sq ft"
    except (IndexError, ValueError):
        utilization = f"{len(bed_plants)} plants in {bed.dimensions}"
        
    return {
        "bed_name": bed.name,
        "total_plants": len(bed_plants),
        "plants_by_status": status_counts,
        "plants_by_season": season_counts,
        "space_utilization": utilization
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