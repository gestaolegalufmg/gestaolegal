ENV ?= development

DC := docker-compose --project-name $(ENV)

ifeq ($(ENV),production)
  COMPOSE_FILES := -f docker-compose.yml -f docker-compose.prod.yml
else ifeq ($(ENV),qa)
  COMPOSE_FILES := -f docker-compose.yml -f docker-compose.prod.yml
else ifeq ($(ENV),test)
  COMPOSE_FILES := -f docker-compose.yml -f docker-compose.qa.yml
else
  COMPOSE_FILES := -f docker-compose.yml -f docker-compose.dev.yml
endif

.PHONY: help up down clean logs exec build initialize_dev_environment

up:
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

initialize_dev_environment:
	@if [ "$(ENV)" = "production" ]; then \
		echo "This command is intended only for non-production environments"; \
	else \
		./scripts/initialize_dev_environment.sh; \
	fi


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
	@echo "  initialize_dev_environment Setup development environment (non-production only)"
