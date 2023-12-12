# Makefile

# Define the path to the docker-compose file
COMPOSE_FILE := docker-compose.yaml
CONTAINER_NAME := worker_sync

# Define the default target
.PHONY: all
all: help

# Define a help message
.PHONY: help
help:
	@echo "Makefile for managing the Docker Compose workflow"
	@echo ""
	@echo "Usage:"
	@echo "  make up                         Start all services"
	@echo "  make down                       Stop all services"
	@echo "  make restart                    Restart all services"
	@echo "  make logs                       View output from containers"
	@echo "  make start-worker-sync          Start worker_sync service"
	@echo "  make start-worker-extract       Start worker_extract service"
	@echo "  make lint                       Run linter"
	@echo "  make fmt                        Run formatter"
	@echo "  make poetry-show-outdated       Show outdated dependencies"
	@echo "  make poetry-update              Update dependencies"
	@echo "  make poetry-lock                Lock dependencies"
	@echo "  make poetry-add                 Add a dependency"
	@echo "  make poetry-remove              Remove a dependency"
	@echo "  make poetry-install             Install dependencies"
	@echo ""

# Start all services
.PHONY: up
up:
	docker-compose -f $(COMPOSE_FILE) up

# Stop all services
.PHONY: down
down:
	docker-compose -f $(COMPOSE_FILE) down

# Restart all services
.PHONY: restart
restart:
	docker-compose -f $(COMPOSE_FILE) restart

# View logs
.PHONY: logs
logs:
	docker-compose -f $(COMPOSE_FILE) logs -f

# Start worker_sync service
.PHONY: start-worker-sync
start-worker-sync:
	docker-compose -f $(COMPOSE_FILE) up worker_sync

# Start worker_extract service
.PHONY: start-worker-extract
start-worker-extract:
	docker-compose -f $(COMPOSE_FILE) up worker_extract

.PHONY: lint
lint:
	docker-compose -f $(COMPOSE_FILE) run --rm $(CONTAINER_NAME) lint

.PHONY: fmt
fmt:
	docker-compose -f $(COMPOSE_FILE) run --rm $(CONTAINER_NAME) fmt

.PHONY: poetry-show-outdated
poetry-show-outdated:
	docker-compose -f $(COMPOSE_FILE) run --rm $(CONTAINER_NAME) poetry show -o -n

.PHONY: poetry-update
poetry-update:
	docker-compose -f $(COMPOSE_FILE) run --rm $(CONTAINER_NAME) poetry update -n $(filter-out $@,$(MAKECMDGOALS))

.PHONY: poetry-lock
poetry-lock:
	docker-compose -f $(COMPOSE_FILE) run --rm $(CONTAINER_NAME) poetry lock

.PHONY: poetry-add
poetry-add:
	docker-compose -f $(COMPOSE_FILE) run --rm $(CONTAINER_NAME) poetry add -n $(filter-out $@,$(MAKECMDGOALS))

.PHONY: poetry-remove
poetry-remove:
	docker-compose -f $(COMPOSE_FILE) run --rm $(CONTAINER_NAME) poetry remove -n $(filter-out $@,$(MAKECMDGOALS))

.PHONY: poetry-install
poetry-install:
	docker-compose -f $(COMPOSE_FILE) run --rm $(CONTAINER_NAME) poetry install

.PHONY: test
test:
	docker-compose -f $(COMPOSE_FILE) run --rm $(CONTAINER_NAME) test

.PHONY: migrate
migrate:
	docker-compose -f $(COMPOSE_FILE) run --rm $(CONTAINER_NAME) migrate

.PHONY: init-db
init-db:
	docker-compose -f $(COMPOSE_FILE) run --rm $(CONTAINER_NAME) init-db

