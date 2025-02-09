#!/bin/bash

# Default values
WATCH_MODE=false
COVERAGE=false
VERBOSE=false
TEST_FILE=""

# Help message
show_help() {
    echo "Usage: ./run-tests-local.sh [OPTIONS] [TEST_FILE]"
    echo "Run tests in Docker container with various options"
    echo ""
    echo "Options:"
    echo "  -w, --watch     Run tests in watch mode"
    echo "  -c, --coverage  Generate coverage report"
    echo "  -v, --verbose   Show verbose output"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run-tests-local.sh                    # Run all tests"
    echo "  ./run-tests-local.sh -w                 # Run tests in watch mode"
    echo "  ./run-tests-local.sh -c                 # Run tests with coverage"
    echo "  ./run-tests-local.sh tests/test_main.py # Run specific test file"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -w|--watch)
            WATCH_MODE=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            TEST_FILE="$1"
            shift
            ;;
    esac
done

# Build the pytest command
PYTEST_ARGS=""

if [ "$VERBOSE" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS -v"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS --cov=src --cov-report=term-missing"
fi

if [ "$WATCH_MODE" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS -f"
fi

if [ -n "$TEST_FILE" ]; then
    PYTEST_ARGS="$PYTEST_ARGS $TEST_FILE"
fi

# Ensure coverage directory exists
mkdir -p coverage

# Run the tests in Docker
if [ "$WATCH_MODE" = true ]; then
    # Watch mode needs terminal interaction
    docker compose -f docker-compose.test.yml run --rm test pytest $PYTEST_ARGS
else
    # Normal mode can use the standard up command
    docker compose -f docker-compose.test.yml up --build --exit-code-from test
fi

# Clean up
docker compose -f docker-compose.test.yml down -v