import os
from dotenv import load_dotenv


load_dotenv()


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

WEBHOOK_PATH_VK = f'/{VK_BOT_TOKEN}'

WEBHOOK_PATH_TG = f'/{TG_BOT_TOKEN}'
TG_BOT_HOST = os.getenv("TG_BOT_HOST", "0.0.0.0")
TG_BOT_PORT = int(os.getenv("TG_BOT_PORT") or 8080)
