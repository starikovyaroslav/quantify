.PHONY: help install install-dev clean lint format type-check test test-cov docker-build docker-up docker-down docker-logs

# Default target
help:
	@echo "QuantTxt - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Install production dependencies"
	@echo "  make install-dev      - Install development dependencies"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             - Run all linters (black, isort, flake8, pylint, mypy)"
	@echo "  make format           - Format code with black and isort"
	@echo "  make type-check       - Run type checking with mypy"
	@echo "  make check            - Run all checks (lint + format check + type-check)"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run tests"
	@echo "  make test-cov         - Run tests with coverage"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     - Build Docker images"
	@echo "  make docker-up        - Start Docker containers"
	@echo "  make docker-down      - Stop Docker containers"
	@echo "  make docker-logs      - Show Docker logs"
	@echo ""
	@echo "Frontend:"
	@echo "  make frontend-install - Install frontend dependencies"
	@echo "  make frontend-lint    - Lint frontend code"
	@echo "  make frontend-format  - Format frontend code"
	@echo "  make frontend-check   - Run all frontend checks"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Remove cache files and build artifacts"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pre-commit install

# Code Quality - Python
lint:
	@echo "Running black check..."
	black --check app tests
	@echo "Running isort check..."
	isort --check-only app tests
	@echo "Running flake8..."
	flake8 app tests
	@echo "Running pylint..."
	pylint app --disable=all --enable=E,F,W,R,C
	@echo "Running mypy..."
	mypy app --ignore-missing-imports
	@echo "✅ All linters passed!"

format:
	@echo "Formatting with black..."
	black app tests
	@echo "Formatting with isort..."
	isort app tests
	@echo "✅ Code formatted!"

type-check:
	@echo "Running mypy..."
	mypy app --ignore-missing-imports
	@echo "✅ Type checking passed!"

check: lint format type-check
	@echo "✅ All checks passed!"

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Docker Development (with hot reload)
docker-dev-up:
	docker-compose -f docker-compose.dev.yml up -d

docker-dev-down:
	docker-compose -f docker-compose.dev.yml down

docker-dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

docker-dev-build:
	docker-compose -f docker-compose.dev.yml build

# Frontend
frontend-install:
	cd frontend && npm install

frontend-lint:
	cd frontend && npm run lint:check

frontend-format:
	cd frontend && npm run format

frontend-type-check:
	cd frontend && npm run type-check

frontend-check:
	cd frontend && npm run check

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -r {} + 2>/dev/null || true
	rm -rf build dist *.egg-info
	rm -rf frontend/.next frontend/out frontend/node_modules/.cache
	@echo "✅ Cleanup complete!"

# Full check (both backend and frontend)
all-check: check frontend-check
	@echo "✅ All checks passed for backend and frontend!"

# Development
dev:
	docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ Development services started with hot reload!"
	@echo "   Backend: http://localhost:8000 (auto-reload on Python changes)"
	@echo "   Frontend: http://localhost:3000 (auto-reload on TypeScript changes)"
	@echo "   Worker: auto-reload on Python changes"

dev-stop:
	docker-compose -f docker-compose.dev.yml down
	@echo "✅ Development services stopped!"

# Production
prod:
	docker-compose up -d
	@echo "✅ Production services started! Backend: http://localhost:8000, Frontend: http://localhost:3000"

prod-stop:
	docker-compose down
	@echo "✅ Production services stopped!"




