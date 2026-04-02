import asyncio
import logging
from celery import shared_task
import sentry_sdk

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def broadcast_tg(self, user_ids, from_chat_id, message_id, admin_chat_id):
    """Рассылка сообщения всем TG-пользователям."""
    from aiogram import Bot
    from unakovskaya_bot.variables import TG_BOT_TOKEN, DELAY_TG_MAIL

    async def _run():
        bot = Bot(token=TG_BOT_TOKEN)
        count = 0
        failed = 0
        try:
            for user_id in user_ids:
                if user_id == admin_chat_id:
                    continue
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
                        "TG broadcast: не удалось отправить "
                        "пользователю %s: %s", user_id, e
                    )

            logger.info(
                "TG broadcast завершён: %d/%d отправлено",
                count, len(user_ids)
            )
            try:
                await bot.send_message(
                    chat_id=admin_chat_id,
                    text=(
                        f"✅ Рассылка завершена.\n"
                        f"Отправлено: {count}\n"
                        f"Ошибок: {failed}"
                    )
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
        api = API(token=VK_BOT_TOKEN)
        count = 0
        failed = 0

        for user_id in user_ids:
            if user_id == from_user_id:
                continue
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
                    "VK broadcast: не удалось отправить "
                    "пользователю %s: %s", user_id, e
                )

        logger.info(
            "VK broadcast завершён: %d/%d отправлено",
            count, len(user_ids)
        )
        try:
            await api.messages.send(
                peer_id=admin_peer_id,
                message=(
                    f"✅ Рассылка завершена.\n"
                    f"Отправлено: {count}\n"
                    f"Ошибок: {failed}"
                ),
                random_id=0
            )
        except Exception:
            pass

        return count

    return asyncio.run(_run())
