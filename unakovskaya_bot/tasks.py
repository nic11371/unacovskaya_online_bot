import asyncio
import logging
from celery import shared_task
import sentry_sdk  # noqa: F401
from unakovskaya_bot.static.texts import TEXTS

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def broadcast_tg(self, user_ids, from_chat_id, message_id, admin_chat_id):
    """Рассылка сообщения всем TG-пользователям."""
    from unakovskaya_bot.variables import DELAY_TG_MAIL
    from unakovskaya_bot.app.clients.tg.bot import create_tg_bot

    async def _run():
        bot = create_tg_bot()
        count = 0
        failed = 0
        try:
            for user_id in user_ids:
                try:
                    await bot.copy_message(
                        chat_id=user_id,
                        from_chat_id=from_chat_id,
                        message_id=message_id
                    )
                    count += 1
                    await asyncio.sleep(DELAY_TG_MAIL)
                except Exception as e:
                    failed += 1
                    logger.warning(
                        TEXTS.get('log_tg_broadcast_fail_user'), user_id, e)

            logger.info(
                TEXTS.get('log_tg_broadcast_done'), count, len(user_ids))
            try:
                await bot.send_message(
                    chat_id=admin_chat_id,
                    text=TEXTS.get('text_broadcast_done').format(
                        count=count, total=len(user_ids))
                )
            except Exception:
                pass
        finally:
            await bot.session.close()

        return count

    return asyncio.run(_run())


@shared_task(bind=True, max_retries=3)
def broadcast_vk(
        self, user_ids, text, attachment_str, from_user_id, admin_peer_id):
    """Рассылка сообщения всем VK-пользователям."""
    from vkbottle import API
    from unakovskaya_bot.variables import VK_BOT_TOKEN, DELAY_VK_MAIL

    async def _run():
        from vkbottle.http import AiohttpClient
        http_client = AiohttpClient()
        api = API(token=VK_BOT_TOKEN, http_client=http_client)
        count = 0
        failed = 0

        try:
            for user_id in user_ids:
                try:
                    await api.messages.send(
                        peer_id=user_id,
                        message=text or "",
                        attachment=attachment_str,
                        random_id=0
                    )
                    count += 1
                    await asyncio.sleep(DELAY_VK_MAIL)
                except Exception as e:
                    failed += 1
                    logger.warning(
                        TEXTS.get('log_vk_broadcast_fail_user'), user_id, e)

            logger.info(
                TEXTS.get('log_vk_broadcast_done'), count, len(user_ids))
            try:
                await api.messages.send(
                    peer_id=admin_peer_id,
                    message=TEXTS.get('text_broadcast_done').format(
                        count=count, total=len(user_ids)),
                    random_id=0
                )
            except Exception as e:
                logger.warning(TEXTS.get('log_vk_broadcast_fail_admin'), e)
        finally:
            await http_client.close()

        return count

    return asyncio.run(_run())
