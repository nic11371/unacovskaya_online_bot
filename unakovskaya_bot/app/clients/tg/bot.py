import socket

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession

from unakovskaya_bot.variables import (
    TG_BOT_CONNECTION_LIMIT,
    TG_BOT_FORCE_IPV4,
    TG_BOT_REQUEST_TIMEOUT,
    TG_BOT_TOKEN,
)


def create_tg_bot() -> Bot:
    """Create a Bot with explicit network settings for Telegram API calls."""
    session = AiohttpSession(
        limit=TG_BOT_CONNECTION_LIMIT,
        timeout=TG_BOT_REQUEST_TIMEOUT,
    )

    if TG_BOT_FORCE_IPV4:
        # aiogram does not expose connector family directly, so we tune it here.
        session._connector_init["family"] = socket.AF_INET

    return Bot(token=TG_BOT_TOKEN, session=session)
