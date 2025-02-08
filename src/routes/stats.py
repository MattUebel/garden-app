from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import pandas as pd
import plotly.express as px
from ..models import GardenStats, PlantStatus, Season, DBPlant, DBGardenBed
from ..database import get_db

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("")
def get_garden_stats(db: Session = Depends(get_db)) -> GardenStats:
    all_plants = db.query(DBPlant).all()
    
    status_counts = {status: 0 for status in PlantStatus}
    season_counts = {season: 0 for season in Season}
    
    for plant in all_plants:
        status_counts[PlantStatus(plant.status)] += 1
        season_counts[Season(plant.season)] += 1
    
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
    
    status_counts = {status: 0 for status in PlantStatus}
    season_counts = {season: 0 for season in Season}
    
    for plant in bed_plants:
        status_counts[PlantStatus(plant.status)] += 1
        season_counts[Season(plant.season)] += 1
        
    return {
        "bed_name": bed.name,
        "total_plants": len(bed_plants),
        "plants_by_status": status_counts,
        "plants_by_season": season_counts,
        "space_utilization": f"{len(bed_plants)} plants in {bed.dimensions}"
    }

@router.get("/charts/plants-by-season")
def get_plants_by_season_chart(db: Session = Depends(get_db)):
    plants = db.query(DBPlant).all()
    df = pd.DataFrame([
        {"season": p.season, "count": 1}
        for p in plants
    ]).groupby("season").sum().reset_index()
    
    fig = px.bar(df, x="season", y="count", title="Plants by Season")
    return JSONResponse(content=fig.to_dict())