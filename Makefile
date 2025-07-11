# Makefile for Docker + Rasa dev/prod

# Default environment
ENV ?= development

# Docker Compose file (single file setup)
COMPOSE_FILE = docker-compose.yml

.PHONY: help
help:
	@echo "Usage:"
	@echo "  make build-dev         - Build in development mode"
	@echo "  make build-prod        - Build in production mode"
	@echo "  make up-dev            - Run dev environment"
	@echo "  make up-prod           - Run production environment"
	@echo "  make down              - Stop and remove containers"
	@echo "  make logs              - View container logs"
	@echo "  make shell             - Open shell in Rasa container"

# Build for development
.PHONY: build-dev
build-dev:
	ENV=development docker compose --compatibility -f $(COMPOSE_FILE) build --build-arg ENV=development

# Build for production
.PHONY: build-prod
build-prod:
	ENV=production docker compose --compatibility -f $(COMPOSE_FILE) build --build-arg ENV=production

# Run dev
.PHONY: up-dev
up-dev:
	ENV=development docker compose -f $(COMPOSE_FILE) up

# Run production
.PHONY: up-prod
up-prod:
	ENV=production docker compose -f $(COMPOSE_FILE) up

# Stop and clean up
.PHONY: down
down:
	docker compose -f $(COMPOSE_FILE) down

# Show logs
.PHONY: logs
logs:
	docker compose -f $(COMPOSE_FILE) logs -f

# Shell into running container
.PHONY: shell
shell:
	docker compose -f $(COMPOSE_FILE) exec rasa /bin/bash

