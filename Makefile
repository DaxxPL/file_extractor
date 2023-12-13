
COMPOSE_FILE := docker-compose.yaml
CONTAINER_NAME := worker_sync
.PHONY: all
all: help

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
	@echo "  make test                       Run tests"
	@echo "  make init-db                    Initialize database"
	@echo ""

.PHONY: up
up:
	docker-compose -f $(COMPOSE_FILE) up

.PHONY: down
down:
	docker-compose -f $(COMPOSE_FILE) down

.PHONY: restart
restart:
	docker-compose -f $(COMPOSE_FILE) restart

.PHONY: logs
logs:
	docker-compose -f $(COMPOSE_FILE) logs -f

.PHONY: start-worker-sync
start-worker-sync:
	docker-compose -f $(COMPOSE_FILE) up worker_sync

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

.PHONY: test
test:
	docker-compose -f $(COMPOSE_FILE) run --rm $(CONTAINER_NAME) test

.PHONY: init-db
init-db:
	docker-compose -f $(COMPOSE_FILE) run --rm $(CONTAINER_NAME) init-db

