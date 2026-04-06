import logging
from vkbottle.bot import Message
from unakovskaya_bot.variables import VK_BOT_USER_ADMIN
from unakovskaya_bot.static.texts import TEXTS
from unakovskaya_bot.app.clients.vk.labeler import chat_labeler
from unakovskaya_bot.app.clients.vk.keyboards.userkb import get_admin_keyboard
from unakovskaya_bot.app.user_services import sync_user, unset_user_admin
from unakovskaya_bot.app.clients.vk.handlers.manage_admin import set_admin
from unakovskaya_bot.app.clients.vk.handlers.manage_links import get_links

logger = logging.getLogger(__name__)


@chat_labeler.message(text=["/start", "Начать", "Start"])
async def start_handler(message: Message):
    try:
        users_info = await message.ctx_api.users.get(
            user_ids=[message.from_id], fields=['domain'])
        user = users_info[0]
    except Exception as e:
        logger.error(
            TEXTS.get('log_vk_start_fail_user_info'), message.from_id, e)
        return

    try:
        await sync_user(
            user_id=user.id,
            platform='vk',
            username=user.domain,
            first_name=user.first_name,
            last_name=user.last_name,
        )
    except Exception as e:
        logger.error(TEXTS.get('log_vk_start_fail_sync'), user.id, e)
        return

    if message.from_id in VK_BOT_USER_ADMIN:
        await set_admin(message)
    else:
        await unset_user_admin(message.from_id, platform='vk')
        await get_links(message)


@chat_labeler.message(payload={"cmd": "welcome_btn"})
async def start_from_button(message: Message):
    # Переиспользуем логику команды /start
    await start_handler(message)


@chat_labeler.message(text="/admin")
async def admin_start(message: Message):
    if message.from_id not in VK_BOT_USER_ADMIN:
        await message.answer(TEXTS.get('text_restrict_admin'))
        return

    await message.answer(
        TEXTS.get('text_admin_panel'), keyboard=get_admin_keyboard())
