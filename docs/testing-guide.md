# Testing Guide

## Running Tests Locally

The project uses pytest with PostgreSQL for testing. You can run tests in several ways:
```bash
# Run all tests
./scripts/run-tests-local.sh

# Run with coverage report
./scripts/run-tests-local.sh -c

# Run specific test file
./scripts/run-tests-local.sh tests/test_plants.py

# Run tests in watch mode (useful during development)
./scripts/run-tests-local.sh -w
```

## Test Configuration

Tests use a dedicated PostgreSQL database specified by the `DATABASE_URL` environment variable. The test infrastructure:
- Creates fresh database tables for each test
- Provides fixtures for database sessions, FastAPI test client, and file storage mocking
- Automatically cleans up after each test
- Handles transaction rollbacks for failed tests

## Test Organization

Tests are organized by feature:
- `test_garden_beds.py`: Garden bed management tests
- `test_plants.py`: Plant management and image upload tests
- `test_stats.py`: Statistics and analytics tests
- `test_main.py`: Core application tests

## Coverage Requirements

- Minimum coverage threshold: 85%
- Branch coverage is enabled
- Coverage reports are generated in multiple formats:
  - HTML report: `coverage/html/index.html`
  - XML report: `coverage/coverage.xml`
  - JSON report: `coverage/coverage.json`
  - Terminal summary
  - JUnit XML report: `coverage/junit.xml`

## CI/CD Pipeline

The test suite runs in GitHub Actions:
- Tests run in Docker for consistent environments
- Coverage reports are uploaded as artifacts
- Coverage badge is automatically updated
- PR comments show coverage changes
- Tests must pass before deployment

## Writing New Tests

When adding new features:
1. Create test file in `tests/` directory
2. Use fixtures from `conftest.py` for database and client setup
3. Follow existing patterns for API testing
4. Ensure error cases are covered
5. Run tests locally with coverage to verify