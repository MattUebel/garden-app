#!/bin/bash
set -e

# Clean up any stale coverage files
rm -f /app/coverage/* /app/.coverage

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

# Ensure coverage directory exists and has proper permissions
mkdir -p /app/coverage
chmod -R 777 /app/coverage

# Run the tests with coverage
echo "Running tests with coverage..."
COVERAGE_FILE=/app/coverage/.coverage pytest --cov=src \
    --cov-report=term-missing \
    --cov-report=html:/app/coverage \
    --cov-report=xml:/app/coverage/coverage.xml \
    --cov-report=json:/app/coverage/coverage.json \
    -v \
    --junitxml=/app/coverage/junit.xml

exit_code=$?

# Ensure coverage files are accessible
chmod -R 777 /app/coverage

# Always generate coverage badge, even on failure
coverage-badge -o /app/coverage/coverage.svg

exit $exit_code