import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from django.core.management.base import BaseCommand
from vkbottle.bot import Bot
from unakovskaya_bot.variables import VK_BOT_TOKEN, SENTRY_DSN
from unakovskaya_bot.app.clients.vk.labeler import chat_labeler
from unakovskaya_bot.app.clients.vk.handlers import commands


class Command(BaseCommand):
    help = "Запуск VK бота"

    def handle(self, *args, **options):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        logger = logging.getLogger(__name__)

        if SENTRY_DSN:
            sentry_sdk.init(
                dsn=SENTRY_DSN,
                integrations=[
                    LoggingIntegration(
                        level=logging.INFO,
                        event_level=logging.ERROR
                    )
                ],
                traces_sample_rate=0.2,
            )
            logger.info("Sentry инициализирован")

        bot = Bot(token=VK_BOT_TOKEN)
        bot.api.state_dispenser = bot.state_dispenser
        bot.labeler.load(chat_labeler)

        logger.info("Запуск VK бота...")
        bot.run_forever()
