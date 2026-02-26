import logging

from django.core.management.base import BaseCommand
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, \
    setup_application
from aiogram.fsm.storage.memory import MemoryStorage
from unakovskaya_bot.variables import \
    TG_BOT_TOKEN, \
    WEBHOOK_PATH_TG, \
    TG_BOT_HOST, \
    TG_BOT_PORT, \
    BASE_URL


class Command(BaseCommand):
    help = "Запускает телеграм-бота в режиме вебхука"

    def handle(self, *args, **options):
        # Настройка логирования
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger = logging.getLogger(__name__)
        logger.info("Запуск телеграм-бота...")

        if not BASE_URL:
            logger.error(
                "Переменная BASE_URL не установлена в .env файле!")
            return

        # Инициализация бота и диспетчера
        bot = Bot(token=TG_BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)

        # Здесь нужно будет зарегистрировать ваши обработчики (хендлеры)
        # Пример:
        # from unakovskaya_bot.app.handlers import user_handlers
        # dp.include_router(user_handlers.router)
        logger.info("Регистрация обработчиков...")

        async def on_startup(bot: Bot):
            """Действия при запуске: установка вебхука."""
            webhook_url = f"{BASE_URL.strip('/')}{WEBHOOK_PATH_TG}"
            await bot.set_webhook(webhook_url)
            logger.info(f"Вебхук установлен на: {webhook_url}")

        async def on_shutdown(bot: Bot):
            """Действия при остановке: удаление вебхука."""
            logger.info("Остановка бота...")
            await bot.delete_webhook(drop_pending_updates=True)
            await bot.session.close()
            logger.info("Вебхук удален.")

        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)

        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp, bot=bot
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH_TG)
        setup_application(app, dp, bot=bot)

        logger.info(f"Запуск на http://{TG_BOT_HOST}:{TG_BOT_PORT}")
        web.run_app(app, host=TG_BOT_HOST, port=TG_BOT_PORT)
