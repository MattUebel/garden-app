from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("garden/beds.html", {"request": request})

@router.get("/garden/beds", response_class=HTMLResponse)
async def garden_beds(request: Request):
    return templates.TemplateResponse("garden/beds.html", {"request": request})

@router.get("/garden/plants", response_class=HTMLResponse)
async def plants(request: Request):
    return templates.TemplateResponse("garden/plants.html", {"request": request})

@router.get("/stats", response_class=HTMLResponse)
async def statistics(request: Request):
    return templates.TemplateResponse("garden/stats.html", {"request": request})

@router.get("/garden/beds/{bed_id}", response_class=HTMLResponse)
async def garden_bed_detail(request: Request, bed_id: int):
    return templates.TemplateResponse("garden/bed_detail.html", {"request": request, "bed_id": bed_id})