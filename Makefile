ENV ?= development

.PHONY: help up down logs exec build initialize_environment

ensure_volumes:
	@echo "Ensuring required directories exist..."
	@mkdir -p /opt/docker_volumes/mysql_data

up: ensure_volumes
	docker compose up -d

run_migrations:
	docker compose exec app_gl bash -c "alembic -c ./migrations/alembic.ini upgrade head"

initialize_environment:
	@if [ "$(ENV)" = "production" ]; then \
		echo "This command is intended only for non-production environments"; \
	else \
		DC="$(DC)" COMPOSE_FILES="$(COMPOSE_FILES)" ./scripts/create_db_procedure.sh; \
		DC="$(DC)" COMPOSE_FILES="$(COMPOSE_FILES)" ./scripts/initialize_environment.sh; \
	fi

tests: up initialize_environment
	pytest --base-url http://localhost:5000 tests/ -vx

test: up initialize_environment
	pytest --base-url http://localhost:5000 tests/ $(file) --headed -vx

tests_dockerized: up initialize_environment
	./scripts/run_tests.sh

help:
	@echo "Usage:"
	@echo ""
	@echo "  make [target] [options]             # Uses default ENV=development"
	@echo "  make ENV=environment [target]       # Set environment inline before target"
	@echo "  ENV=environment make [target]       # Set environment as shell variable"
	@echo "  export ENV=environment; make [target]  # Set as persistent shell variable"
	@echo ""
	@echo "Environments:"
	@echo "  development (default)"
	@echo "  production"
	@echo ""
	@echo "Targets:"
	@echo "  help                       Show this help message"
	@echo "  up                         Start containers in detached mode"
	@echo "  initialize_environment Setup environment (non-production only)"
