from fastapi import APIRouter, HTTPException, Path, Body, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import (
    GardenBed, Plant, Season, PlantStatus,
    DBGardenBed, DBPlant
)

router = APIRouter(prefix="/garden", tags=["garden"])

VALID_STATUS_TRANSITIONS = {
    PlantStatus.PLANTED: [PlantStatus.SPROUTED],
    PlantStatus.SPROUTED: [PlantStatus.FLOWERING],
    PlantStatus.FLOWERING: [PlantStatus.HARVESTING],
    PlantStatus.HARVESTING: [PlantStatus.FINISHED],
    PlantStatus.FINISHED: []
}

@router.post("/beds")
def create_garden_bed(garden_bed: GardenBed, db: Session = Depends(get_db)) -> GardenBed:
    db_bed = DBGardenBed(
        name=garden_bed.name,
        dimensions=garden_bed.dimensions,
        notes=garden_bed.notes
    )
    db.add(db_bed)
    db.commit()
    db.refresh(db_bed)
    return GardenBed(
        id=db_bed.id,
        name=db_bed.name,
        dimensions=db_bed.dimensions,
        notes=db_bed.notes,
        plants=[]
    )

@router.get("/beds")
def list_garden_beds(db: Session = Depends(get_db)) -> list[GardenBed]:
    db_beds = db.query(DBGardenBed).all()
    return [
        GardenBed(
            id=bed.id,
            name=bed.name,
            dimensions=bed.dimensions,
            notes=bed.notes,
            plants=[]
        )
        for bed in db_beds
    ]

@router.get("/beds/{bed_id}")
def get_garden_bed(bed_id: int, db: Session = Depends(get_db)) -> GardenBed:
    db_bed = db.query(DBGardenBed).filter(DBGardenBed.id == bed_id).first()
    if not db_bed:
        raise HTTPException(status_code=404, detail="Garden bed not found")
    
    return GardenBed(
        id=db_bed.id,
        name=db_bed.name,
        dimensions=db_bed.dimensions,
        notes=db_bed.notes,
        plants=[
            Plant(
                id=p.id,
                name=p.name,
                variety=p.variety,
                planting_date=p.planting_date,
                location=f"Bed {db_bed.id}",
                status=PlantStatus(p.status),
                season=Season(p.season),
                expected_harvest_date=p.expected_harvest_date,
                notes=p.notes
            )
            for p in db_bed.plants
        ]
    )

@router.post("/plants")
def create_plant(plant: Plant, db: Session = Depends(get_db)) -> Plant:
    # Extract bed ID from location string
    try:
        bed_id = int(plant.location.split()[1])
    except (IndexError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Invalid location. Must be in format 'Bed N' where N is an existing garden bed ID"
        )
    
    # Verify bed exists
    db_bed = db.query(DBGardenBed).filter(DBGardenBed.id == bed_id).first()
    if not db_bed:
        raise HTTPException(status_code=404, detail="Garden bed not found")
    
    db_plant = DBPlant(
        name=plant.name,
        variety=plant.variety,
        planting_date=plant.planting_date,
        bed_id=bed_id,
        status=plant.status.value,
        season=plant.season.value,
        expected_harvest_date=plant.expected_harvest_date,
        notes=plant.notes
    )
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    
    return Plant(
        id=db_plant.id,
        name=db_plant.name,
        variety=db_plant.variety,
        planting_date=db_plant.planting_date,
        location=f"Bed {bed_id}",
        status=PlantStatus(db_plant.status),
        season=Season(db_plant.season),
        expected_harvest_date=db_plant.expected_harvest_date,
        notes=db_plant.notes
    )

@router.get("/plants")
def list_plants(season: Season = None, db: Session = Depends(get_db)) -> list[Plant]:
    query = db.query(DBPlant)
    if season:
        query = query.filter(DBPlant.season == season.value)
    
    return [
        Plant(
            id=p.id,
            name=p.name,
            variety=p.variety,
            planting_date=p.planting_date,
            location=f"Bed {p.bed_id}",
            status=PlantStatus(p.status),
            season=Season(p.season),
            expected_harvest_date=p.expected_harvest_date,
            notes=p.notes
        )
        for p in query.all()
    ]

@router.patch("/plants/{plant_id}/status")
def update_plant_status(
    plant_id: int,
    new_status: PlantStatus = Body(..., embed=True),
    db: Session = Depends(get_db)
) -> Plant:
    db_plant = db.query(DBPlant).filter(DBPlant.id == plant_id).first()
    if not db_plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    current_status = PlantStatus(db_plant.status)
    if new_status not in VALID_STATUS_TRANSITIONS[current_status]:
        valid_transitions = VALID_STATUS_TRANSITIONS[current_status]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition. From {current_status.value}, can only transition to: {[s.value for s in valid_transitions]}"
        )
    
    db_plant.status = new_status.value
    db.commit()
    db.refresh(db_plant)
    
    return Plant(
        id=db_plant.id,
        name=db_plant.name,
        variety=db_plant.variety,
        planting_date=db_plant.planting_date,
        location=f"Bed {db_plant.bed_id}",
        status=PlantStatus(db_plant.status),
        season=Season(db_plant.season),
        expected_harvest_date=db_plant.expected_harvest_date,
        notes=db_plant.notes
    )