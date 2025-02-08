# Garden App
A FastAPI-based garden management system that helps track and manage your garden beds, plants, and their growth.

## Features
- Garden bed management and tracking
- Plant lifecycle monitoring
- Image upload and processing
- Barcode scanning support
- Garden statistics and visualization
- RESTful API endpoints
- Responsive web interface

## Prerequisites
- Python 3.11+
- pip or pipenv
- Docker (optional)
- PostgreSQL (if not using Docker)

## Getting Started

### Raspberry Pi Setup
1. Install system dependencies:
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib libpq-dev gcc python3-dev
```

2. Create and configure PostgreSQL database:
```bash
sudo -u postgres createuser pi
sudo -u postgres createdb garden_db
sudo -u postgres psql
    ALTER USER pi WITH PASSWORD 'your_password';
    GRANT ALL PRIVILEGES ON DATABASE garden_db TO pi;
```

3. Clone and set up the application:
```bash
git clone git@github.com:MattUebel/garden-app.git
cd garden-app
python3 -m venv venv
source venv/bin/activate
pip install wheel  # Install wheel first to help with binary dependencies
pip install -r requirements.txt
```

4. Create a .env file:
```bash
DATABASE_URL=postgresql://pi:your_password@localhost:5432/garden_db
```

5. Run the application:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

6. (Optional) Set up as a system service:
```bash
# Copy the service file
sudo cp scripts/garden-app.service /etc/systemd/system/
sudo systemctl daemon-reload

# Start the service
sudo systemctl start garden-app

# Enable at boot
sudo systemctl enable garden-app

# Check status
sudo systemctl status garden-app
```

You can view the logs using:
```bash
sudo journalctl -u garden-app -f
```

The application will be available at `http://<raspberry-pi-ip>:8000`

> Note: For running on Raspberry Pi, we recommend using the local installation method rather than Docker due to better ARM processor support and reduced overhead.

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
pip install -r dev-requirements.txt  # For development tools

# Or using pipenv
pipenv install
pipenv shell
```

3. Set up environment variables (create a .env file):
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/garden_db
```

4. Run the application:
```bash
uvicorn main:app --reload
```

### Using Docker
1. Build and run with Docker:
```bash
# Using Docker Compose V2 (recommended)
docker compose up --build

# Or using individual commands
docker build -t garden-app .
docker run -p 8000:8000 garden-app
```

The application will be available at http://localhost:8000

> Note: This project uses Docker Compose V2. The `docker-compose` command (with a hyphen) is legacy and has been replaced by `docker compose` in modern Docker installations.

## API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Project Structure
```
garden-app/
├── main.py              # Application entry point
├── requirements.txt     # Production dependencies
├── dev-requirements.txt # Development dependencies
├── Dockerfile          # Docker configuration
├── compose.yaml        # Docker Compose V2 configuration
├── src/               # Source code modules
│   ├── database.py    # Database configuration
│   ├── models.py      # Database models
│   └── routes/        # API route handlers
│       ├── frontend.py
│       ├── garden.py
│       ├── images.py
│       └── stats.py
├── static/            # Static assets
│   ├── css/
│   └── js/
├── templates/         # HTML templates
│   ├── base.html
│   └── garden/
└── tests/            # Test files
```

### Running Tests
```bash
pytest
```

### Code Style
The project follows PEP 8 guidelines. To maintain code quality:

1. Install development dependencies:
```bash
pip install -r dev-requirements.txt
```

2. Run linting:
```bash
flake8
```

3. Run type checking:
```bash
mypy .
```

## Cloud Deployment

### Azure Deployment Options

1. **Azure App Service (Recommended)**
   - Supports Python web apps with built-in CI/CD
   - Easy scaling and monitoring
   - Deploy using:
   ```bash
   az webapp up --runtime PYTHON:3.11 --sku B1 --name your-garden-app
   ```

2. **Azure Container Apps**
   - Containerized deployment using existing Docker setup
   - Serverless container runtime with auto-scaling
   - Deploy using:
   ```bash
   # Build and push to Azure Container Registry
   docker build -t your-acr.azurecr.io/garden-app:latest .
   docker push your-acr.azurecr.io/garden-app:latest
   
   # Deploy to Container Apps
   az containerapp up --name your-garden-app --resource-group your-rg --image your-acr.azurecr.io/garden-app:latest
   ```

3. **Azure Kubernetes Service (AKS)**
   - For larger scale deployments
   - Full container orchestration
   - Use existing docker-compose.yml with Docker Desktop's Kubernetes

### Required Azure Resources
- Azure Database for PostgreSQL
- Azure Storage Account (for image storage)
- Azure Container Registry (if using containers)

### Environment Configuration
Add these to your Azure App Service Configuration:
```
DATABASE_URL=postgresql://<user>:<password>@<server-name>.postgres.database.azure.com:5432/garden_db
AZURE_STORAGE_CONNECTION_STRING=<your-storage-connection-string>
```

For detailed Azure deployment instructions, see our [Azure Deployment Guide](docs/azure-deployment.md)

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure they pass
5. Submit a pull request

## License
This project is licensed under the MIT License.
