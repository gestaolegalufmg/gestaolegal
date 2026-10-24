COMPOSE_DEV = docker compose -f docker-compose.dev.yml

.PHONY: up test test-cov test-watch seed

seed:
	uv run python scripts/seed_database.py $(ARGS)

up:
	$(COMPOSE_DEV) up -d --build

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
	@echo "  seed                Seed development database (ARGS='--dry-run' to preview)"
	@echo "  test                Run API tests"
	@echo "  test-cov            Run API tests with coverage report"
	@echo "  test-watch          Run tests in watch mode"
