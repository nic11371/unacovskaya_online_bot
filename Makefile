sync:
	uv sync

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
