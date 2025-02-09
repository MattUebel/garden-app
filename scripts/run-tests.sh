#!/bin/bash
set -e

echo "Waiting for postgres to be ready..."
# Wait for postgres to be ready
for i in {1..30}; do
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h postgres -U $POSTGRES_USER -d postgres -c '\l' | grep -q garden_db; then
        echo "Database garden_db exists - postgres is ready"
        break
    fi
    echo "Waiting for postgres to be ready and database to be created... ($i/30)"
    sleep 2
    if [ $i = 30 ]; then
        echo "Timeout waiting for postgres"
        exit 1
    fi
done

echo "Postgres is up - executing database setup"
python -c "
from src.database import Base, engine
from src.models import DBGardenBed, DBPlant, DBPlantImage  # Import all models
Base.metadata.drop_all(bind=engine)  # Clean slate
Base.metadata.create_all(bind=engine)  # Create all tables
"

# Verify tables exist
echo "Verifying database tables..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h postgres -U $POSTGRES_USER -d garden_db -c '\dt'

# Run the tests with coverage
echo "Running tests with coverage..."
pytest --cov=src \
    --cov-report=term-missing \
    --cov-report=html:/app/coverage \
    --cov-report=xml:/app/coverage/coverage.xml \
    --cov-report=json:coverage/coverage.json \
    -v \
    --junitxml=/app/coverage/junit.xml

exit_code=$?

# Always generate coverage badge, even on failure
coverage-badge -o /app/coverage/coverage.svg

exit $exit_code