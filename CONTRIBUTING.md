# Contributing to Garden App

We love your input! We want to make contributing to Garden App as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## We Develop with GitHub
We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## We Use [GitHub Flow](https://guides.github.com/introduction/flow/index.html)
Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Development Process
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r dev-requirements.txt
```

3. Setup pre-commit hooks:
```bash
pre-commit install
```

4. Make your changes and ensure they pass all checks:
```bash
pytest
flake8
mypy .
```

## Testing Guidelines

### Writing Tests

1. All new features must include corresponding tests
2. Tests should be placed in the `tests/` directory following the existing structure
3. Use the provided fixtures from `conftest.py`:
   - `engine`: Database engine fixture
   - `test_db`: Database session fixture
   - `client`: FastAPI TestClient fixture
   - `mock_storage`: File storage mock fixture

### Test Best Practices

1. Use descriptive test names that explain the scenario being tested
2. Follow the Arrange-Act-Assert pattern
3. Test both success and error cases
4. Mock external dependencies using fixtures
5. Keep tests focused and atomic
6. Use parameterized tests for multiple similar scenarios

### Running Tests

Before submitting a PR:
1. Ensure all tests pass locally
2. Check the coverage report
3. Add new tests for any new functionality
4. Verify existing tests aren't broken

### Database Testing

- Tests use a dedicated PostgreSQL database
- Each test gets a fresh database state
- Transactions are automatically rolled back
- Use the `test_db` fixture for database access

## Local Development Environment
1. Set up PostgreSQL database
2. Copy `.env.example` to `.env` and configure your environment variables
3. Run migrations: `alembic upgrade head`
4. Start the development server: `uvicorn main:app --reload`

## Any contributions you make will be under the MIT Software License
In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issue tracker](https://github.com/MattUebel/garden-app/issues)
We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/MattUebel/garden-app/issues/new/choose).

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## License
By contributing, you agree that your contributions will be licensed under its MIT License.