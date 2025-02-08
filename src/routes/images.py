from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import io
from datetime import datetime
from PIL import Image
from pyzbar.pyzbar import decode
from ..models import PlantImage, BarcodeData, DBPlant, DBPlantImage
from ..database import get_db

router = APIRouter(prefix="/images", tags=["images"])

@router.post("/plants/{plant_id}/upload")
async def upload_plant_image(
    plant_id: int,
    file: UploadFile = File(...),
    description: str = None,
    db: Session = Depends(get_db)
) -> PlantImage:
    plant = db.query(DBPlant).filter(DBPlant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    # In production, save image to cloud storage and return URL
    # For demo, we'll pretend we saved it
    image_url = f"http://example.com/images/{file.filename}"
    
    db_image = DBPlantImage(
        url=image_url,
        description=description,
        taken_date=datetime.now(),
        plant_id=plant_id
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    return PlantImage(
        url=db_image.url,
        description=db_image.description,
        taken_date=db_image.taken_date
    )

@router.post("/scan-barcode")
async def scan_barcode(file: UploadFile = File(...)) -> BarcodeData:
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    barcodes = decode(image)
    
    if not barcodes:
        raise HTTPException(status_code=400, detail="No barcode found in image")
    
    barcode = barcodes[0]
    return BarcodeData(
        code=barcode.data.decode(),
        type=barcode.type,
    )