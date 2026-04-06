import logging
import sentry_sdk
from aiohttp import ClientTimeout
from sentry_sdk.integrations.logging import LoggingIntegration
from django.core.management.base import BaseCommand
from vkbottle.bot import Bot
from vkbottle.api import API
from vkbottle.http import AiohttpClient
from unakovskaya_bot.static.texts import TEXTS
from unakovskaya_bot.variables import VK_BOT_TOKEN, SENTRY_DSN
from unakovskaya_bot.app.clients.vk.labeler import chat_labeler
from unakovskaya_bot.app.clients.vk.handlers import (  # noqa: F401
    commands, manage_links, manage_admin, manage_broadcast, manage_settings
)


class Command(BaseCommand):
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
            logger.info(TEXTS.get("text_log_sentry"))

        # sock_read=35 чуть больше VK Long Poll wait=25,
        # чтобы не было TimeoutError
        http_client = AiohttpClient(
            timeout=ClientTimeout(total=None, connect=30, sock_read=35)
        )
        import unakovskaya_bot.app.clients.vk.labeler as vk_labeler
        api = API(token=VK_BOT_TOKEN, http_client=http_client)
        bot = Bot(api=api)
        bot.labeler.load(chat_labeler)
        vk_labeler.state_dispenser = bot.state_dispenser

        logger.info(TEXTS.get("text_start_vk_bot"))
        bot.run_forever()
