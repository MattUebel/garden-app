from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, HttpUrl

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

class BarcodeData(BaseModel):
    code: str
    type: str
    product_name: Optional[str] = None
    manufacturer: Optional[str] = None

class PlantImage(BaseModel):
    url: HttpUrl
    description: Optional[str] = None
    taken_date: datetime

class Plant(BaseModel):
    id: Optional[int]
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
    id: Optional[int]
    name: str
    dimensions: str
    plants: List[Plant] = []
    notes: Optional[str] = None

class GardenStats(BaseModel):
    total_plants: int
    plants_by_status: dict[PlantStatus, int]
    plants_by_season: dict[Season, int]
