import asyncio
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from unakovskaya_bot.variables import TG_BOT_USER_ADMIN
from unakovskaya_bot.static.texts import TEXTS
from unakovskaya_bot.app.videolinks_services import get_active_links
from unakovskaya_bot.app.clients.tg.keyboards.userkb import start_btn
from unakovskaya_bot.app.user_services import sync_user, set_user_admin


user = Router()


@user.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await sync_user(
        user_id=message.from_user.id,
        platform='tg',
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    button = start_btn()

    # 1. Отправляем приветствие
    await message.answer(TEXTS.get('welcome'), reply_markup=button)

    try:
        admin_id = int(TG_BOT_USER_ADMIN)
    except (ValueError, TypeError):
        admin_id = None

    if admin_id and admin_id == message.from_user.id:
        await set_user_admin(message.from_user.id)
        await message.answer("👨‍💻 Вы опознаны как администратор.\nВведите /admin для входа в панель управления.")
    else:
        # 2. Получаем и отправляем ссылки постепенно (только если не админ)
        links = await get_active_links()
        if links:
            for link in links:
                await asyncio.sleep(5)
                text_part = f"{link.order}. {link.title}\n{link.message_text}\n🔗 {link.url}"
                await message.answer(text_part)
        else:
            await message.answer(TEXTS.get('no_links'))
