# Unacovskaya Online Bot

Бот для автоматической рассылки обучающих материалов (ссылок) пользователям в **Telegram** и **ВКонтакте**. Администратор управляет контентом и пользователями через встроенную админ-панель прямо в боте.

---

## Функционал

### Для пользователей

- Получение серии обучающих материалов бот последовательно отправляет ссылки с описаниями
- Между материалами выдерживается пауза (настраивается), с возможностью пропустить её кнопкой «Готово»
- После определённого шага бот запрашивает email пользователя без него следующий материал не отправляется
- После ввода email следующий материал присылается сразу, без ожидания

### Для администратора

Доступ к панели: `/admin`

| Кнопка | Действие |
|---|---|
| Написать анонс | Рассылка сообщения (текст, фото, видео) всем пользователям |
| ➕ Добавить ссылку | Добавить новый материал (название, ссылка, описание) |
| 📋 Список (Удалить) | Просмотр всех материалов с возможностью удаления |
| Получить емайлы | Скачать файл `emails.txt` со всеми собранными email-адресами |
| ⚙️ Шаг запроса email | Изменить номер шага, после которого запрашивается email |

---

## Стек

- **Python 3.12**
- **Django** — ORM, модели, управление БД
- **aiogram 3** — Telegram бот
- **vkbottle** — ВКонтакте бот
- **aiohttp** — загрузка файлов в VK
- **Celery** — фоновые задачи (рассылка)
- **Redis** — брокер задач для Celery
- **PostgreSQL** (или SQLite для разработки)
- **uv** — менеджер зависимостей

---

## Запуск через Docker (рекомендуется)

Самый простой способ — запустить всё сразу через Docker Compose. Он поднимает PostgreSQL, Redis, миграции, оба бота и Celery-воркер автоматически.

### 1. Клонировать репозиторий

```bash
git clone <repo_url>
cd unacovskaya_online_bot
```

### 2. Создать файл `.env`

```bash
cp .env_example .env
```

Заполнить обязательные переменные (токены ботов, ID администраторов, параметры БД).

### 3. Собрать и запустить

```bash
make docker-build
make docker-up
```

Или одной командой:

```bash
docker compose up -d --build
```

Миграции применяются автоматически при старте.

### Полезные команды

| Команда | Описание |
|---|---|
| `make docker-up` | Запустить все сервисы в фоне |
| `make docker-up-tg-foreign` | Запустить только foreign TG стек |
| `make docker-down` | Остановить все сервисы |
| `make docker-down-tg-foreign` | Остановить foreign TG стек |
| `make docker-restart` | Перезапустить все сервисы |
| `make docker-logs` | Смотреть логи всех сервисов |
| `make docker-logs-tg-foreign` | Смотреть логи foreign TG стека |
| `docker compose logs -f vk-bot` | Логи только VK бота |
| `docker compose logs -f tg-bot` | Логи только TG бота |
| `docker compose logs -f celery` | Логи Celery-воркера |

### Сервисы

| Сервис | Описание |
|---|---|
| `db` | PostgreSQL |
| `redis` | Redis (брокер Celery) |
| `migrate` | Применение миграций (запускается один раз) |
| `web` | Django web, admin и internal API |
| `tg-bot` | Telegram бот |
| `vk-bot` | ВКонтакте бот |
| `celery` | Воркер для рассылок |

## Двухсерверная схема

Если Telegram недоступен с основного сервера, можно вынести `tg-bot` на foreign VPS.

### Что где живет

- Основной сервер: `web`, `db`, `redis`, `vk-bot`, основной `celery`
- Foreign VPS: `tg-bot`, `celery-tg`, локальный `redis`

### Как они общаются

- `tg-bot` обращается к Telegram API напрямую с foreign VPS
- `tg-bot` обращается к основному Django через защищенный `internal-api`
- Аутентификация между серверами идет через заголовок `X-Internal-Token`

### 1. Основной сервер

Запустите Django web, чтобы были доступны admin и `internal-api`:

```bash
docker compose up -d web db redis migrate vk-bot celery
```

Добавьте в `.env` на основном сервере:

```env
INTERNAL_API_TOKEN=replace_with_long_random_secret
WEB_PORT=8000
ALLOWED_HOSTS=app.example.com,127.0.0.1,localhost
```

Потом отдайте `web:8000` наружу через Nginx или другой reverse proxy.

### 2. Foreign VPS

Скопируйте проект на foreign VPS и создайте `.env` по примеру:

```bash
cp .env.foreign.example .env
```

Минимально заполните:

```env
TG_BOT_TOKEN=...
TG_BOT_USER_ADMIN=...
BASE_URL=https://tg-bot.example.com

APP_API_BASE_URL=https://app.example.com
APP_API_TOKEN=replace_with_same_long_random_secret

REDIS_URL=redis://redis:6379/0
TG_BOT_FORCE_IPV4=true
TG_BOT_REQUEST_TIMEOUT=120
```

Запуск:

```bash
docker compose -f docker-compose.tg-foreign.yml up -d --build
```

### 3. Что уже переключается автоматически

Если задан `APP_API_BASE_URL`, Telegram хендлеры больше не ходят напрямую в Django ORM. Они автоматически переключаются на HTTP backend через `internal-api`.

Это касается:

- синхронизации пользователей
- проверки и выдачи админских прав
- чтения и удаления ссылок
- настроек шага и текста запроса email
- сохранения email
- выгрузки email
- получения списка TG пользователей для рассылки

---

## Локальный запуск (для разработки)

### 1. Клонировать репозиторий

```bash
git clone <repo_url>
cd unacovskaya_online_bot
```

### 2. Установить зависимости

```bash
make sync
```

### 3. Создать файл `.env`

Пример переменных в `.env_example`. Для разработки можно использовать SQLite:

```env
DATABASE_ENGINE=sqlite
DATABASE_NAME=db.sqlite3
REDIS_URL=redis://localhost:6379/0
```

### 4. Запустить Redis локально

```bash
redis-server
```

Или через Docker (только Redis):

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### 5. Применить миграции

```bash
make migrate
```

### 6. Запустить компоненты (каждый в отдельном терминале)

Django (опционально, для веб-админки):
```bash
make start
```

Telegram бот:
```bash
make start-tg
```

ВКонтакте бот:
```bash
make start-vk
```

Celery-воркер (обязателен для рассылок):
```bash
make start-celery
```

---

## Переменные окружения

| Переменная | Описание | По умолчанию |
|---|---|---|
| `TG_BOT_TOKEN` | Токен Telegram бота | — |
| `VK_BOT_TOKEN` | Токен группы ВКонтакте | — |
| `TG_BOT_USER_ADMIN` | Telegram ID администратора | — |
| `VK_BOT_USER_ADMIN` | VK ID администратора | — |
| `DELAY_LINK` | Пауза между материалами (секунды) | `5` |
| `DELAY_TG_MAIL` | Задержка между сообщениями при рассылке TG (секунды) | `0.2` |
| `DELAY_VK_MAIL` | Задержка между сообщениями при рассылке VK (секунды) | `0.2` |
| `EMAIL_AFTER_STEP` | Шаг, после которого запрашивается email (начальное значение) | `3` |
| `EMAIL_TIMEOUT` | Время ожидания ввода email пользователем (секунды) | `600` |
| `WEB_PORT` | Порт Django web / internal API | `8000` |
| `APP_API_BASE_URL` | Базовый URL основного Django для foreign TG бота | `""` |
| `APP_API_TOKEN` | Токен доступа foreign TG бота к internal API | `""` |
| `APP_API_TIMEOUT` | Таймаут запросов foreign TG бота к internal API | `30` |
| `INTERNAL_API_TOKEN` | Токен защиты internal API на основном сервере | `""` |
| `TG_BOT_REQUEST_TIMEOUT` | Таймаут исходящих запросов к Telegram API | `60` |
| `TG_BOT_CONNECTION_LIMIT` | Лимит одновременных TG-соединений | `100` |
| `TG_BOT_FORCE_IPV4` | Принудительный IPv4 для Telegram API | `false` |

> Шаг запроса email можно менять прямо из админ-панели бота — значение сохраняется в БД и применяется без перезапуска.

---

## Структура материалов

Каждый материал содержит:
- **Порядковый номер** (шаг)
- **Название**
- **Ссылка**
- **Описание**

Материалы добавляются через админ-панель бота (`/admin` веб-интерфейс).
