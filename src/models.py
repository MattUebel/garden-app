from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, HttpUrl
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from .database import Base

class Season(str, Enum):
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"

class PlantStatus(str, Enum):
    PLANTED = "planted"
    SPROUTED = "sprouted"
    FLOWERING = "flowering"
    HARVESTING = "harvesting"
    FINISHED = "finished"

class BarcodeType(str, Enum):
    QR = "QR"
    CODE128 = "CODE128"
    EAN13 = "EAN13"
    UPC = "UPC"

class BarcodeData(BaseModel):
    code: str
    type: BarcodeType
    product_name: Optional[str] = None
    manufacturer: Optional[str] = None

class PlantImage(BaseModel):
    url: HttpUrl
    description: Optional[str] = None
    taken_date: datetime

class Plant(BaseModel):
    id: Optional[int] = None
    name: str
    variety: Optional[str] = None
    planting_date: datetime
    location: str  # Location in garden
    status: PlantStatus
    season: Season
    expected_harvest_date: Optional[datetime] = None
    images: List[PlantImage] = []
    notes: Optional[str] = None
    seed_packet_barcode: Optional[BarcodeData] = None

class GardenBed(BaseModel):
    id: Optional[int] = None
    name: str
    dimensions: str
    plants: List[Plant] = []
    notes: Optional[str] = None

class GardenStats(BaseModel):
    total_plants: int
    plants_by_status: dict[PlantStatus, int]
    plants_by_season: dict[Season, int]

class DBGardenBed(Base):
    __tablename__ = "garden_beds"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String)
    dimensions = sa.Column(sa.String)
    notes = sa.Column(sa.String, nullable=True)
    plants = relationship("DBPlant", back_populates="garden_bed")

class DBPlant(Base):
    __tablename__ = "plants"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String)
    variety = sa.Column(sa.String, nullable=True)
    planting_date = sa.Column(sa.DateTime)
    bed_id = sa.Column(sa.Integer, sa.ForeignKey("garden_beds.id"))
    status = sa.Column(sa.String)
    season = sa.Column(sa.String)
    expected_harvest_date = sa.Column(sa.DateTime, nullable=True)
    notes = sa.Column(sa.String, nullable=True)
    garden_bed = relationship("DBGardenBed", back_populates="plants")
    images = relationship("DBPlantImage", back_populates="plant")

class DBPlantImage(Base):
    __tablename__ = "plant_images"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    url = sa.Column(sa.String)
    description = sa.Column(sa.String, nullable=True)
    taken_date = sa.Column(sa.DateTime)
    plant_id = sa.Column(sa.Integer, sa.ForeignKey("plants.id"))
    plant = relationship("DBPlant", back_populates="images")
