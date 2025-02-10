# Contributing to Garden App

We love your input! We want to make contributing to Garden App as easy and transparent as possible.

## Development Process

1. Fork the repo and create your branch from `main`
2. Set up your development environment following our [Development Guide](docs/development-guide.md)
3. Make your changes
4. Ensure your code follows our style guidelines:
   ```bash
   flake8
   mypy .
   ```
5. Run the test suite as described in our [Testing Guide](docs/testing-guide.md)
6. Update documentation if needed

## Pull Request Process

1. Update the README.md or relevant documentation with details of changes
2. Verify that all CI checks pass
3. Add yourself to CONTRIBUTORS.md if you aren't already listed

## Code Style

- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Document functions and classes using docstrings
- Keep functions focused and single-purpose
- Use meaningful variable names

## Testing Requirements

- Write tests for new features
- Maintain or improve code coverage
- See [Testing Guide](docs/testing-guide.md) for details

## Documentation

Update documentation when you:
- Add or modify features
- Change existing functionality
- Fix bugs that affect user behavior

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Reference issues and pull requests liberally

## Issues

### Creating Issues

- Use issue templates when available
- Provide clear reproduction steps for bugs
- Include relevant system information
- Attach screenshots if applicable

### Working on Issues

1. Comment on the issue to claim it
2. Create a branch with format: `type/issue-description`
   - Types: feature/, bugfix/, docs/, test/
3. Reference the issue in commits and PR

## Getting Help

- Check the documentation first
- Search existing issues
- Ask questions in pull requests or issues
- Join our community chat

## License

By contributing, you agree that your contributions will be licensed under the MIT License.