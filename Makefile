ENV ?= development

DC := docker compose --project-name $(ENV)

ifeq ($(ENV),production)
  COMPOSE_FILES := -f docker-compose.yml -f docker-compose.prod.yml
else ifeq ($(ENV),qa)
  COMPOSE_FILES := -f docker-compose.yml -f docker-compose.prod.yml
else ifeq ($(ENV),test)
  COMPOSE_FILES := -f docker-compose.yml -f docker-compose.test.yml
else
  COMPOSE_FILES := -f docker-compose.yml -f docker-compose.dev.yml
endif

.PHONY: help up down clean logs exec build initialize_environment

ensure_volumes:
	@echo "Ensuring required directories exist..."
	@mkdir -p /opt/docker_volumes/mysql_data

up: ensure_volumes
	$(DC) $(COMPOSE_FILES) up -d

down:
	$(DC) $(COMPOSE_FILES) down

clean:
	@if [ "$(ENV)" = "production" ]; then \
		echo "This command is intended only for non-production environments"; \
	else \
		$(DC) $(COMPOSE_FILES) down -v; \
	fi

logs:
	$(DC) $(COMPOSE_FILES) logs -f || true

exec:
	$(DC) $(COMPOSE_FILES) exec -ti $(service) $(cmd)

build:
	$(DC) $(COMPOSE_FILES) build

initialize_environment:
	@if [ "$(ENV)" = "production" ]; then \
		echo "This command is intended only for non-production environments"; \
	else \
		DC="$(DC)" COMPOSE_FILES="$(COMPOSE_FILES)" ./scripts/initialize_environment.sh; \
	fi

run_test:
	pytest --ignore=mysql_data/

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
	@echo "  test"
	@echo "  qa"
	@echo "  production"
	@echo ""
	@echo "Targets:"
	@echo "  help                       Show this help message"
	@echo "  up                         Start containers in detached mode"
	@echo "  down                       Stop containers"
	@echo "  clean                      Stop containers and remove volumes (non-production only)"
	@echo "  logs                       View container logs (follow mode)"
	@echo "  exec service=NAME cmd=CMD  Execute command in a container"
	@echo "  build                      Build or rebuild containers"
	@echo "  initialize_environment Setup environment (non-production only)"
