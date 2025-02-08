# Garden Manager API

A FastAPI-based application for managing garden beds, plants, and tracking their growth through images and statistics.

## Features

- Garden bed management
- Plant tracking with seasonal information
- Image upload support
- Barcode scanning
- Garden statistics and charts
- RESTful API endpoints

## Requirements

See requirements.txt for a full list of dependencies.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once running, visit:
- http://localhost:8000/docs for Swagger UI documentation
- http://localhost:8000/redoc for ReDoc documentation