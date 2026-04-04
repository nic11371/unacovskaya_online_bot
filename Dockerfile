FROM python:3.12-slim

# Копируем uv из официального образа
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Устанавливаем зависимости (используем lock-файл для воспроизводимости)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Копируем весь проект
COPY . .
