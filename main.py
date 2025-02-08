from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import io
from datetime import datetime
import plotly.express as px
import pandas as pd
from PIL import Image
from pyzbar.pyzbar import decode
from models import (
    MsgPayload, Plant, GardenBed, PlantStatus, Season, BarcodeData,
    PlantImage, GardenStats
)

app = FastAPI()
messages_list: dict[int, MsgPayload] = {}
garden_beds: dict[int, GardenBed] = {}
plants: dict[int, Plant] = {}


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome to Garden Manager API"}


# About page route
@app.get("/about")
def about() -> dict[str, str]:
    return {"message": "This is the about page."}


# Route to add a message
@app.post("/messages/{msg_name}/")
def add_msg(msg_name: str) -> dict[str, MsgPayload]:
    # Generate an ID for the item based on the highest ID in the messages_list
    msg_id = max(messages_list.keys()) + 1 if messages_list else 0
    messages_list[msg_id] = MsgPayload(msg_id=msg_id, msg_name=msg_name)

    return {"message": messages_list[msg_id]}


# Route to list all messages
@app.get("/messages")
def message_items() -> dict[str, dict[int, MsgPayload]]:
    return {"messages:": messages_list}


@app.post("/garden-beds/")
def create_garden_bed(garden_bed: GardenBed) -> GardenBed:
    bed_id = len(garden_beds)
    garden_bed.id = bed_id
    garden_beds[bed_id] = garden_bed
    return garden_bed


@app.get("/garden-beds/")
def list_garden_beds() -> list[GardenBed]:
    return list(garden_beds.values())


@app.post("/plants/")
def create_plant(plant: Plant) -> Plant:
    plant_id = len(plants)
    plant.id = plant_id
    plants[plant_id] = plant
    return plant


@app.get("/plants/")
def list_plants(season: Season = None) -> list[Plant]:
    if season:
        return [p for p in plants.values() if p.season == season]
    return list(plants.values())


@app.post("/plants/{plant_id}/images/")
async def upload_plant_image(
    plant_id: int,
    file: UploadFile = File(...),
    description: str = None
) -> PlantImage:
    if plant_id not in plants:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    # In production, save image to cloud storage and return URL
    # For demo, we'll pretend we saved it
    image_url = f"http://example.com/images/{file.filename}"
    
    plant_image = PlantImage(
        url=image_url,
        description=description,
        taken_date=datetime.now()
    )
    plants[plant_id].images.append(plant_image)
    return plant_image


@app.post("/scan-barcode/")
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


@app.get("/stats/")
def get_garden_stats() -> GardenStats:
    all_plants = list(plants.values())
    
    status_counts = {}
    for status in PlantStatus:
        status_counts[status] = len([p for p in all_plants if p.status == status])
    
    season_counts = {}
    for season in Season:
        season_counts[season] = len([p for p in all_plants if p.season == season])
    
    return GardenStats(
        total_plants=len(all_plants),
        plants_by_status=status_counts,
        plants_by_season=season_counts
    )


@app.get("/charts/plants-by-season")
def get_plants_by_season_chart():
    df = pd.DataFrame([
        {"season": p.season, "count": 1}
        for p in plants.values()
    ]).groupby("season").sum().reset_index()
    
    fig = px.bar(df, x="season", y="count", title="Plants by Season")
    return JSONResponse(content=fig.to_dict())
