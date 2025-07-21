.PHONY: help install install-dev test test-integration lint format type-check clean docs serve-docs playwright-install

# Default target
help:
	@echo "ITA Scrapper Development Commands"
	@echo "================================="
	@echo ""
	@echo "Setup:"
	@echo "  install           Install package for production"
	@echo "  install-dev       Install package with development dependencies"
	@echo "  playwright-install Install Playwright browsers"
	@echo ""
	@echo "Development:"
	@echo "  test              Run unit tests"
	@echo "  test-integration  Run integration tests (slow)"
	@echo "  test-all          Run all tests including integration"
	@echo "  lint              Run linting (ruff)"
	@echo "  format            Format code with black"
	@echo "  type-check        Run type checking with mypy"
	@echo "  check-all         Run all checks (lint, format, type-check)"
	@echo ""
	@echo "Documentation:"
	@echo "  docs              Build documentation"
	@echo "  serve-docs        Serve documentation locally"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean             Clean build artifacts"
	@echo "  clean-all         Clean everything including cache"

# Installation
install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"
	uv pip install -r requirements-dev.txt

playwright-install:
	playwright install
	playwright install-deps

# Testing
test:
	pytest -v --tb=short -x -m "not integration"

test-integration:
	pytest -v --tb=short -m "integration"

test-all:
	pytest -v --tb=short

test-cov:
	pytest --cov=src/ita_scrapper --cov-report=html --cov-report=term

# Code quality
lint:
	ruff check src/ tests/ examples/

lint-fix:
	ruff check --fix src/ tests/ examples/

format:
	black src/ tests/ examples/

format-check:
	black --check src/ tests/ examples/

type-check:
	mypy src/ita_scrapper

check-all: lint format-check type-check

# Documentation  
docs:
	mkdocs build

serve-docs:
	mkdocs serve

# Maintenance
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-all: clean
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf test-results/
	rm -rf playwright-report/

# Pre-commit
pre-commit-install:
	pre-commit install

pre-commit-run:
	pre-commit run --all-files

# Build and publish (for CI/CD)
build:
	python -m build

publish-test:
	python -m twine upload --repository testpypi dist/*

publish:
	python -m twine upload dist/*

# Development workflow
dev-setup: install-dev playwright-install pre-commit-install
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify everything is working."

# Quick development checks
quick-check: format lint type-check test
	@echo "All quick checks passed! ✅"
