import logging
from django.core.management.base import BaseCommand
from vkbottle.bot import Bot
from unakovskaya_bot.variables import VK_BOT_TOKEN
from unakovskaya_bot.app.clients.vk.labeler import chat_labeler
# Импортируем модуль с хендлерами, чтобы декораторы в нем выполнились
from unakovskaya_bot.app.clients.vk.handlers import commands


class Command(BaseCommand):
    help = "Запуск VK бота"

    def handle(self, *args, **options):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger = logging.getLogger(__name__)

        # Инициализация бота
        bot = Bot(token=VK_BOT_TOKEN)

        # Загружаем хендлеры из внешних файлов (через labeler)
        # Теперь chat_labeler не пустой, т.к. модуль commands был импортирован
        bot.labeler.load(chat_labeler)

        logger.info("Запуск VK бота...")
        bot.run_forever()
