from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from unakovskaya_bot.static.texts import TEXTS
from unakovskaya_bot.app.services import get_formatted_links_text
from unakovskaya_bot.app.clients.tg.keyboards.userkb import start_btn
from unakovskaya_bot.app.clients.tg.utils.requests import set_user, \
    save_info_user


user = Router()


@user.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await set_user(message.from_user.id)
    await save_info_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    button = start_btn()

    # Получаем текст со ссылками из общего сервиса
    links_text = await get_formatted_links_text()
    welcome_msg = TEXTS["welcome"]
    full_text = f"{welcome_msg}\n\n{links_text}" \
        if links_text else TEXTS["no_links"]

    await message.answer(
        full_text, reply_markup=button)
