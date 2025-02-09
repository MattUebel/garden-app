from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
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

# Create an API router for all API routes
api_app = FastAPI(title="Garden Manager API")

# Include all API routes
api_app.include_router(garden.router)
api_app.include_router(images.router)
api_app.include_router(stats.router)

# Root route for API
@api_app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello"}

@api_app.get("/about")
def about() -> dict[str, str]:
    return {"message": "This is the about page."}

# Mount the API under /api
app.mount("/api", api_app)

# Include UI routes
app.include_router(frontend.router)

# Root redirect
@app.get("/")
async def redirect_to_ui():
    return RedirectResponse(url="/ui")

@app.get("/health")
def health_check():
    return {"status": "healthy"}
