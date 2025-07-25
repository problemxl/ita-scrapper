# Contributing

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/problemxl/ita-scrapper
   cd ita-scrapper
   ```

2. **Install development dependencies:**
   ```bash
   uv pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

## Code Standards

### Style Guide
- Follow PEP 8 with 88-character line limit
- Use type hints for all functions
- Use Pydantic models for data validation
- Prefer composition over inheritance

### Naming Conventions
- Functions and variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private attributes: `_leading_underscore`

### Documentation
- Use Google-style docstrings
- Include examples in docstrings
- Document all parameters and return values
- Add type hints to all function signatures

## Testing

### Running Tests
```bash
# All tests
uv run pytest -v

# Specific test
uv run pytest -v -k "test_search_flights"

# Integration tests only
uv run pytest -v -m integration

# With coverage
uv run pytest --cov=src/ita_scrapper --cov-report=html
```

### Writing Tests
- Place tests in the `tests/` directory
- Mirror the `src/` structure in test organization
- Use descriptive test names: `test_should_parse_flight_when_valid_html`
- Mock external dependencies (browser automation, network calls)
- Use fixtures for common test data

### Test Categories
- **Unit tests**: Fast, isolated, no external dependencies
- **Integration tests**: Test component interactions
- **End-to-end tests**: Full workflow testing (marked with `@pytest.mark.integration`)

## Code Quality

### Linting and Formatting
```bash
# Check code style
uv run ruff check src/ tests/

# Auto-fix style issues
uv run ruff check --fix src/ tests/

# Format code
uv run ruff format src/ tests/

# Type checking
uv run mypy src/ita_scrapper
```

### Pre-commit Hooks
The project uses pre-commit hooks to ensure code quality:
- **ruff**: Code formatting and linting
- **mypy**: Type checking
- **gitleaks**: Security scanning
- **conventional-commit**: Commit message format

## Submitting Changes

### Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write code following the style guide
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes:**
   ```bash
   uv run pytest -v
   uv run ruff check --fix src/ tests/
   uv run mypy src/ita_scrapper
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add new search functionality"
   ```

5. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format
Use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions/modifications
- `refactor:` Code refactoring
- `style:` Formatting changes
- `chore:` Maintenance tasks

### PR Guidelines
- Provide clear description of changes
- Include test coverage for new features
- Update documentation if needed
- Ensure CI passes
- Request review from maintainers

## Architecture Guidelines

### Adding New Features

1. **Models First**: Define Pydantic models for new data structures
2. **Parser Extension**: Extend parsing logic for new data extraction
3. **API Integration**: Add methods to main scrapper class
4. **Error Handling**: Define specific exceptions for new failure modes
5. **Documentation**: Add docstrings and usage examples

### Backward Compatibility
- Maintain API compatibility in minor versions
- Use deprecation warnings before removing features
- Provide migration guides for breaking changes

### Performance Considerations
- Profile parsing performance for large result sets
- Consider caching for expensive operations
- Optimize browser automation efficiency
- Monitor memory usage during long-running operations

## Release Process

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Create release tag**: `git tag v1.2.0`
4. **Push tag**: `git push origin v1.2.0`
5. **GitHub Actions** will automatically publish to PyPI

## Getting Help

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Security**: Email security issues to maintainers privately
- **Documentation**: Improve docs via pull requests