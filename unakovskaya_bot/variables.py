import os
from dotenv import load_dotenv


load_dotenv()


TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
VK_BOT_TOKEN = os.getenv("VK_BOT_TOKEN")
SECRET_KEY = os.getenv("SECRET_KEY")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS")
DEBUG = os.getenv("DEBUG")

ENGINE_DB = os.getenv("ENGINE")
NAME_DB = os.getenv("NAME")
USER_DB = os.getenv("USER")
PASSWORD_DB = os.getenv("PASSWORD")
HOST_DB = os.getenv('HOST_DB')
PORT_DB = os.getenv('PORT_DB')

BASE_URL = os.getenv("BASE_URL")

WEBHOOK_PATH_VK = f'/{VK_BOT_TOKEN}'

WEBHOOK_PATH_TG = f'/{TG_BOT_TOKEN}'
TG_BOT_HOST = os.getenv("TG_BOT_HOST", "0.0.0.0")
TG_BOT_PORT = int(os.getenv("TG_BOT_PORT") or 8080)
