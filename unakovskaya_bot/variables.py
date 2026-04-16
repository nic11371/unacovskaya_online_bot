import os
from dotenv import load_dotenv


load_dotenv()


def env_to_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
VK_BOT_TOKEN = os.getenv("VK_BOT_TOKEN")
SECRET_KEY = os.getenv("SECRET_KEY")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS")
DEBUG = os.getenv("DEBUG")

DATABASE_ENGINE = os.getenv("DATABASE_ENGINE")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')

BASE_URL = os.getenv("BASE_URL")
APP_API_BASE_URL = os.getenv("APP_API_BASE_URL", "").rstrip("/")
APP_API_TOKEN = os.getenv("APP_API_TOKEN", "")
APP_API_TIMEOUT = float(os.getenv("APP_API_TIMEOUT") or 30)
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "")

WEBHOOK_PATH_VK = f'/{VK_BOT_TOKEN}'
VK_BOT_USER_ADMIN = {int(x) for x in os.getenv('VK_BOT_USER_ADMIN', '').split(',') if x.strip()}

WEBHOOK_PATH_TG = f'/{TG_BOT_TOKEN}'
TG_BOT_HOST = os.getenv("TG_BOT_HOST", "0.0.0.0")
TG_BOT_PORT = int(os.getenv("TG_BOT_PORT") or 8080)
TG_BOT_USER_ADMIN = {int(x) for x in os.getenv('TG_BOT_USER_ADMIN', '').split(',') if x.strip()}
TG_BOT_REQUEST_TIMEOUT = float(os.getenv('TG_BOT_REQUEST_TIMEOUT') or 60)
TG_BOT_CONNECTION_LIMIT = int(os.getenv('TG_BOT_CONNECTION_LIMIT') or 100)
TG_BOT_FORCE_IPV4 = env_to_bool(os.getenv('TG_BOT_FORCE_IPV4'), False)

DELAY_LINK = int(os.getenv('DELAY_LINK') or 5)
DELAY_TG_MAIL = float(os.getenv('DELAY_TG_MAIL') or 0.2)
DELAY_VK_MAIL = float(os.getenv('DELAY_VK_MAIL') or 0.2)

EMAIL_AFTER_STEP = int(os.getenv('EMAIL_AFTER_STEP') or 3)
EMAIL_TIMEOUT = int(os.getenv('EMAIL_TIMEOUT') or 600)

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
SENTRY_DSN = os.getenv('SENTRY_DSN', '')
