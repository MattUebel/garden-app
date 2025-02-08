from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.routes import garden, images, stats, frontend
from src.database import engine
from src.models import Base

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Garden Manager",
    description="A web application for managing garden beds and plants",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes under /api prefix
app.include_router(garden.router, prefix="/api")
app.include_router(images.router, prefix="/api")
app.include_router(stats.router, prefix="/api")

# Include frontend routes at root level
app.include_router(frontend.router)

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome to Garden Manager API"}

@app.get("/about")
def about() -> dict[str, str]:
    return {"message": "This is the about page."}
