# Garden App

[![CI/CD](https://github.com/MattUebel/garden-app/actions/workflows/ci.yml/badge.svg)](https://github.com/MattUebel/garden-app/actions/workflows/ci.yml)

A FastAPI-based garden management system that helps track and manage your garden beds, plants, and their growth.

## Features

- Garden bed management and tracking
- Plant lifecycle monitoring with yearly tracking
- Image upload and processing
- Barcode scanning support
- Garden statistics and visualization, including year-over-year comparisons
- RESTful API endpoints
- Responsive web interface

## Quick Start

### Prerequisites
- Docker and Docker Compose V2
- Git

### Local Development

1. Clone the repository:
```bash
git clone git@github.com:MattUebel/garden-app.git
cd garden-app
```

2. Start the development environment:
```bash
docker compose up
```

The application will be available at http://localhost:8000. The development server will automatically reload when you make changes to the code.

> Note: Database data is persisted in a Docker volume named "garden-app-db-data". The development database is accessible on port 5432 with username "garden_user" and password "garden_password" if you need to connect directly.

## Documentation

- [Development Guide](docs/development-guide.md)
- [Testing Guide](docs/testing-guide.md)
- [Azure Deployment Guide](docs/azure-deployment.md)
- [Raspberry Pi Deployment Guide](docs/raspberry-pi-deployment.md)

## API Documentation
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License.
