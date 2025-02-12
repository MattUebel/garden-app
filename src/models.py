from typing import Optional, List
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, HttpUrl, validator, Field
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from .database import Base

class PlantStatus(str, Enum):
    PLANTED = "PLANTED"
    SPROUTED = "SPROUTED"
    FLOWERING = "FLOWERING"
    HARVESTING = "HARVESTING"
    FINISHED = "FINISHED"

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
    year: Optional[int] = Field(default_factory=lambda: datetime.now().year)  # Default to current year
    quantity: int = 1
    space_required: Optional[int] = Field(default=4, description="Space required per plant in square inches")
    expected_harvest_date: Optional[datetime] = None
    images: List[PlantImage] = []
    notes: Optional[str] = None
    seed_packet_barcode: Optional[BarcodeData] = None

    @validator('planting_date', 'expected_harvest_date', pre=True)
    def parse_date(cls, value):
        if isinstance(value, (date, datetime)):
            return value
        try:
            return datetime.fromisoformat(value) if value else None
        except (TypeError, ValueError):
            return datetime.strptime(value, '%Y-%m-%d') if value else None

    @validator('quantity')
    def validate_quantity(cls, v):
        if v < 1:
            raise ValueError('Quantity must be at least 1')
        return v

    @validator('year')
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v < 2000 or v > current_year + 1:  # Allow planning for next year
            raise ValueError(f'Year must be between 2000 and {current_year + 1}')
        return v

class GardenBed(BaseModel):
    id: Optional[int] = None
    name: str
    dimensions: str
    plants: List[Plant] = []
    notes: Optional[str] = None

    @validator('dimensions')
    def validate_dimensions(cls, v):
        import re
        if not re.match(r'^[1-9]\d*x[1-9]\d*$', v):
            raise ValueError('Dimensions must be in format LxW where L and W are positive integers')
        return v

class GardenStats(BaseModel):
    total_plants: int
    plants_by_status: dict[PlantStatus, int]

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
    year = sa.Column(sa.Integer)  # New column
    quantity = sa.Column(sa.Integer, default=1)
    space_required = sa.Column(sa.Integer, default=4)
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
