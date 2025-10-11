ENV ?= development

.PHONY: help up down logs exec build initialize_environment

ensure_volumes:
	@echo "Ensuring required directories exist..."
	@mkdir -p /opt/docker_volumes/mysql_data

up: ensure_volumes
	docker compose up -d

run_migrations:
	docker compose exec app_gl sh -c "alembic -c ./migrations/alembic.ini upgrade head"


test:
	uv run pytest tests/api/ -v

test-cov:
	uv run pytest tests/api/ --cov=gestaolegal --cov-report=html --cov-report=term

test-watch:
	uv run pytest tests/api/ -v --looponfail

help:
	@echo "Usage:"
	@echo ""
	@echo "  make [target] [options]"
	@echo ""
	@echo "Targets:"
	@echo "  help                Show this help message"
	@echo "  up                  Start containers in detached mode"
	@echo "  run_migrations      Run database migrations"
	@echo "  test                Run API tests"
	@echo "  test-cov            Run API tests with coverage report"
	@echo "  test-watch          Run tests in watch mode"
