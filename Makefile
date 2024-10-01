# Makefile

# Variables
DOCKER_COMPOSE = docker-compose
FLASK = docker-compose exec web flask

# Default target
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make build        Build the Docker images"
	@echo "  make up           Start the Docker containers"
	@echo "  make down         Stop the Docker containers"
	@echo "  make migrate      Run database migrations"
	@echo "  make initdb       Initialize the database (first-time setup)"
	@echo "  make shell        Open a shell in the web container"
	@echo "  make logs         View logs of all services"
	@echo "  make clean        Remove Docker containers and volumes"
	@echo "  make restart      Rebuild and restart the application"
	@echo "  make test         Run tests (if applicable)"

# Build Docker images
.PHONY: build
build:
	$(DOCKER_COMPOSE) build

# Start containers
.PHONY: up
up:
	$(DOCKER_COMPOSE) up

# Start containers in detached mode
.PHONY: up-detached
up-detached:
	$(DOCKER_COMPOSE) up -d

# Stop containers
.PHONY: down
down:
	$(DOCKER_COMPOSE) down

# Run database migrations
.PHONY: migrate
migrate:
	$(FLASK) db upgrade

# Create migration scripts (if models have changed)
.PHONY: makemigrations
makemigrations:
	$(FLASK) db migrate

# Initialize the database (first-time setup)
.PHONY: initdb
initdb:
	$(FLASK) db init
	$(FLASK) db migrate
	$(FLASK) db upgrade

# Open a shell in the web container
.PHONY: shell
shell:
	$(DOCKER_COMPOSE) exec web sh

# View logs
.PHONY: logs
logs:
	$(DOCKER_COMPOSE) logs -f

# Clean up containers and volumes
.PHONY: clean
clean:
	$(DOCKER_COMPOSE) down -v

# Rebuild and restart the application
.PHONY: restart
restart:
	$(DOCKER_COMPOSE) down
	$(DOCKER_COMPOSE) build
	$(DOCKER_COMPOSE) up

# Run tests (if you have tests set up)
.PHONY: test
test:
	$(DOCKER_COMPOSE) exec web pytest

# Stop and remove all containers, images, and volumes (use with caution)
.PHONY: nuke
nuke:
	$(DOCKER_COMPOSE) down --rmi all -v --remove-orphans

