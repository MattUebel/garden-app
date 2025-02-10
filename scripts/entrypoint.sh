#!/bin/bash
# Execute database migrations
alembic upgrade head

# Start the application
exec "$@"