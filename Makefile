COMPOSE_FILE=infra/docker-compose.yml
ENV_FILE=.env
TEST_ENV_FILE=.env.test

.PHONY: bootstrap up down logs ps migrate makemigration seed worker-run test test-api test-worker

bootstrap:
	@if [ ! -f $(ENV_FILE) ]; then cp .env.example $(ENV_FILE); fi

up:
	docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) up -d --build

down:
	docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) down

logs:
	docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) logs -f --tail=200

ps:
	docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) ps

migrate:
	docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) run --rm api alembic upgrade head

makemigration:
	@echo "Usage: make makemigration name=create_xxx"
	docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) run --rm api alembic revision --autogenerate -m "$(name)"

seed:
	docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) run --rm api python -m app.seed

worker-run:
	docker compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) run --rm worker python worker.py run-daily-episode

test:
	@if [ ! -f $(TEST_ENV_FILE) ]; then echo "Missing $(TEST_ENV_FILE). Create it from .env.test.example"; exit 1; fi
	docker compose -f $(COMPOSE_FILE) --env-file $(TEST_ENV_FILE) up -d --build postgres api worker
	docker compose -f $(COMPOSE_FILE) --env-file $(TEST_ENV_FILE) run --rm api alembic upgrade head
	docker compose -f $(COMPOSE_FILE) --env-file $(TEST_ENV_FILE) run --rm api pytest -q tests

test-api:
	@if [ ! -f $(TEST_ENV_FILE) ]; then echo "Missing $(TEST_ENV_FILE). Create it from .env.test.example"; exit 1; fi
	docker compose -f $(COMPOSE_FILE) --env-file $(TEST_ENV_FILE) up -d --build postgres api worker
	docker compose -f $(COMPOSE_FILE) --env-file $(TEST_ENV_FILE) run --rm api alembic upgrade head
	docker compose -f $(COMPOSE_FILE) --env-file $(TEST_ENV_FILE) run --rm api pytest -q tests/test_health.py tests/test_auth.py tests/test_episodes.py

test-worker:
	@if [ ! -f $(TEST_ENV_FILE) ]; then echo "Missing $(TEST_ENV_FILE). Create it from .env.test.example"; exit 1; fi
	docker compose -f $(COMPOSE_FILE) --env-file $(TEST_ENV_FILE) up -d --build postgres api worker
	docker compose -f $(COMPOSE_FILE) --env-file $(TEST_ENV_FILE) run --rm api alembic upgrade head
	docker compose -f $(COMPOSE_FILE) --env-file $(TEST_ENV_FILE) run --rm api pytest -q tests/test_worker_media_flow.py
