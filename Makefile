sync:
	uv sync

init:
	uv init

migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

start:
	python manage.py runserver

app:
	python manage.py startapp $(name)

lint:
	uv run ruff check .

format:
	uv run ruff format .
