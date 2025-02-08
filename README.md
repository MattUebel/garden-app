# Garden App

A FastAPI-based garden management system that helps track and manage your garden beds, plants, and their growth.

## Features

- Garden bed management and tracking
- Plant lifecycle monitoring
- Image upload and processing
- Barcode scanning support
- Garden statistics and visualization
- RESTful API endpoints

## Prerequisites

- Python 3.11+
- pip or pipenv
- Docker (optional)

## Getting Started

### Local Development

1. Clone the repository:
```bash
git clone git@github.com:MattUebel/garden-app.git
cd garden-app
```

2. Set up your environment:
```bash
# Using pip
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Or using pipenv
pipenv install
pipenv shell
```

3. Run the application:
```bash
uvicorn main:app --reload
```

### Using Docker

1. Build the container:
```bash
docker build -t garden-app .
```

2. Run the container:
```bash
docker run -p 8000:8000 garden-app
```

The API will be available at http://localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Running Tests
```bash
pytest
```

### Project Structure

```
garden-app/
├── main.py           # Main application entry point
├── models.py         # Database models
├── src/             # Source code modules
└── tests/           # Test files
