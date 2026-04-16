sync:
	uv sync

docker-build:
	docker compose build

docker-build-tg-foreign:
	docker compose -f docker-compose.tg-foreign.yml build

docker-up:
	docker compose up -d

docker-up-tg-foreign:
	docker compose -f docker-compose.tg-foreign.yml up -d

docker-down:
	docker compose down

docker-down-tg-foreign:
	docker compose -f docker-compose.tg-foreign.yml down

docker-logs:
	docker compose logs -f

docker-logs-tg-foreign:
	docker compose -f docker-compose.tg-foreign.yml logs -f

docker-restart:
	docker compose down && docker compose up -d

init:
	uv init

migrations:
	uv run python manage.py makemigrations

migrate:
	uv run python manage.py migrate

start:
	uv run python manage.py runserver

start-tg:
	uv run python manage.py run_tg_bot

start-vk:
	uv run python manage.py run_vk_bot

start-celery:
	uv run celery -A unakovskaya_bot worker --loglevel=info

lint:
	uv run ruff check .

format:
	uv run ruff format .
