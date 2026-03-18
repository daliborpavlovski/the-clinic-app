.PHONY: up down seed migrate logs test restart build clean help

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up:  ## Start all services
	docker compose up -d
	@echo "Waiting for services to be healthy…"
	@sleep 3
	@docker compose exec backend alembic upgrade head
	@echo "✅ The Clinic App is up at http://localhost"
	@echo "   Swagger UI: http://localhost/docs"

down:  ## Stop all services
	docker compose down

build:  ## Rebuild images
	docker compose build --no-cache

restart:  ## Restart all services
	docker compose restart

seed:  ## Seed the database with test data
	docker compose exec backend python -m scripts.seed_db

migrate:  ## Run Alembic migrations
	docker compose exec backend alembic upgrade head

logs:  ## Tail all logs
	docker compose logs -f

logs-backend:  ## Tail backend logs
	docker compose logs -f backend

test:  ## Run backend unit tests
	docker compose exec backend python -m pytest tests/ -v

clean:  ## Remove volumes and containers
	docker compose down -v --remove-orphans
