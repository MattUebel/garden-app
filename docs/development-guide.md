# Development Guide

## Project Structure
```
garden-app/
├── .github/            # GitHub configuration and CI/CD workflows
├── alembic/            # Database migrations and configuration
├── docs/              # Project documentation
├── scripts/           # Utility and deployment scripts
├── src/               # Source code
│   ├── database.py    # Database configuration
│   ├── models.py      # Database models
│   └── routes/        # API route handlers
├── static/            # Web assets (CSS, JavaScript)
├── templates/         # HTML templates
├── tests/             # Test suite
├── main.py            # Application entry point
├── compose.yaml       # Docker Compose configuration
├── docker-compose.test.yml  # Test environment configuration
├── Dockerfile         # Main container configuration
├── Dockerfile.test    # Test container configuration
├── README.md          # Project overview and quick start
├── CONTRIBUTING.md    # Contribution guidelines
├── .gitignore        # Git ignore patterns
├── dev-requirements.txt  # Development dependencies
├── requirements.txt   # Production dependencies
├── alembic.ini       # Database migration config
└── pyproject.toml    # Python project config
```

## Development Environment

### Prerequisites
- Docker and Docker Compose V2
- Git
- Your favorite code editor with Python support

### Setting Up Your Environment

1. Clone the repository:
```bash
git clone git@github.com:MattUebel/garden-app.git
cd garden-app
```

2. Start the development environment:
```bash
docker compose up
```

The application will be available at http://localhost:8000. The development server automatically reloads when you make changes to the code.

### Development Database

The PostgreSQL database is available at:
- Host: localhost
- Port: 5432
- Database: garden_db
- User: garden_user
- Password: garden_password (override with DB_PASSWORD environment variable)

### Environment Customization

Configure the development environment using these options:

1. Database password:
```bash
DB_PASSWORD=your_secure_password docker compose up
```

2. Memory limits (in compose.yaml):
- Web service: 512MB limit, 256MB reservation
- Database: 512MB limit, 256MB reservation

### Container Health Monitoring

The environment includes health checks for both services:

- Web service: Checks `/health` endpoint every 30s
- Database: Checks PostgreSQL connection every 10s

You can monitor health status with:
```bash
docker compose ps
```

> Note: If you haven't started the containers yet with `docker compose up`, the above command will show no running containers. This is expected.

### API Health Endpoint

The application exposes a `/health` endpoint that returns basic health information:
```bash
curl http://localhost:8000/health
```

This endpoint is used by Docker for container health checks every 30 seconds. A 200 status code indicates the service is healthy.

### Code Style

The project follows PEP 8 guidelines. Run style checks inside the container:

```bash
docker compose exec web flake8
docker compose exec web mypy .
```

### Architecture Notes

1. The web service automatically reloads code changes thanks to the volume mount:
```yaml
volumes:
  - .:/app
```
This means both Python code changes and requirement changes (after running pip install) will be picked up automatically.

2. The database is multi-architecture compatible and runs on:
- linux/amd64
- linux/arm64
- linux/arm/v7

3. The Docker image uses multi-stage builds to minimize size:
- Build stage: Includes gcc and build dependencies for compiling wheels
- Runtime stage: Only includes required runtime libraries
- Pre-built wheels for numpy and pandas improve build times

4. The database uses postgres:15-alpine which supports:
- linux/amd64
- linux/arm64
- linux/arm/v7
Ensuring consistent development across different CPU architectures.

### Route Organization

The application uses two main route prefixes:

### Frontend Routes (`/ui`)
- `/ui/` - Home page
- `/ui/garden/beds` - Garden beds overview
- `/ui/garden/plants` - Plants management
- `/ui/stats` - Statistics dashboard
- `/ui/garden/beds/{bed_id}` - Bed detail view

### API Routes (`/api`)
All API endpoints are mounted under `/api`. Major endpoints include:

Garden Beds:
- `POST /api/garden/beds` - Create a garden bed
- `GET /api/garden/beds` - List all garden beds
- `GET /api/garden/beds/{bed_id}` - Get a specific bed
- `PATCH /api/garden/beds/{bed_id}` - Update a bed

Plants:
- `POST /api/garden/plants` - Create a plant
- `GET /api/garden/plants` - List plants (optional season/year filters)
- `GET /api/garden/plants/{plant_id}` - Get a specific plant
- `PATCH /api/garden/plants/{plant_id}` - Update plant details
- `PATCH /api/garden/plants/{plant_id}/status` - Update plant status
- `DELETE /api/garden/plants/{plant_id}` - Delete a plant

Full API documentation is available at `/api/docs`

### Static Files
Static assets are served directly:
- CSS: `/static/css/main.css`
- JavaScript: `/static/js/main.js`

### Troubleshooting

1. If you need to rebuild the containers:
```bash
docker compose up --build
```

2. To view logs:
```bash
docker compose logs -f
```

3. To reset the database:
```bash
docker compose down -v
docker compose up
```

4. To check API health manually:
```bash
docker compose exec web curl -f http://localhost:8000/health