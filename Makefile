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

lint:
	uv run ruff check .

format:
	uv run ruff format .
