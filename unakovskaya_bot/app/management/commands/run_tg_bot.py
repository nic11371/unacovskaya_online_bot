import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from django.core.management.base import BaseCommand
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, \
    setup_application
from aiogram.fsm.storage.redis import RedisStorage
from unakovskaya_bot.static.texts import TEXTS
from unakovskaya_bot.variables import (
    TG_BOT_TOKEN, WEBHOOK_PATH_TG,
    TG_BOT_HOST, TG_BOT_PORT, BASE_URL,
    REDIS_URL, SENTRY_DSN
)
from unakovskaya_bot.app.clients.tg.router import router
from unakovskaya_bot.app.clients.tg.handlers import (  # noqa: F401
    commands, manage_links, manage_admin, manage_broadcast, manage_settings
)


class Command(BaseCommand):
    help = TEXTS.get('text_log_help')

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

        logger.info(TEXTS.get('text_log_start'))

        if not BASE_URL:
            logger.error(TEXTS.get('text_log_variable_err'))
            return

        bot = Bot(token=TG_BOT_TOKEN)
        storage = RedisStorage.from_url(REDIS_URL)
        dp = Dispatcher(storage=storage)

        dp.include_router(router)
        logger.info(TEXTS.get('text_log_register'))

        async def on_startup(bot: Bot):
            domain = BASE_URL.strip('/')
            webhook_url = f"{domain}{WEBHOOK_PATH_TG}"
            await bot.set_webhook(webhook_url)
            logger.info(
                "%s %s", TEXTS.get('text_log_webhook_set'), webhook_url)

        async def on_shutdown(bot: Bot):
            logger.info(TEXTS.get('text_log_stop_bot'))
            await bot.delete_webhook(drop_pending_updates=True)
            await bot.session.close()
            logger.info(TEXTS.get('text_log_webhook_rem'))

        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)

        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp, bot=bot
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH_TG)
        setup_application(app, dp, bot=bot)

        logger.info(
            "%s%s:%s", TEXTS.get('text_log_http'), TG_BOT_HOST, TG_BOT_PORT)
        web.run_app(app, host=TG_BOT_HOST, port=TG_BOT_PORT)
