## ITA Scrapper Development Guide

### Package Management
- Use `uv` for all package management
- Install deps: `uv pip install -e ".[dev]"
- Sync lockfile: `uv pip sync requirements-dev.txt`

### Build/Test Commands
- Run tests: `uv run pytest -v` (all) or `uv run pytest -v -k "test_name"` (single)
- Integration tests: `uv run pytest -v -m integration`
- Lint/fix: `uv run ruff check --fix src/ tests/`
- Format: `uv run ruff format src/ tests/`
- Type check: `uv run mypy src/ita_scrapper`

### Code Style
- Line length: 88 characters
- Use type hints for all functions
- Imports: stdlib first, then third-party, then local
- Use Pydantic models for validation
- Naming: snake_case for functions/variables, PascalCase for classes
- Error handling: Specific exceptions with Pydantic validation

### Pre-commit & CI
- Pre-commit hooks: ruff, mypy, gitleaks
- Test CI locally: `act`
- Pre-commit checks: formatting, types, security
