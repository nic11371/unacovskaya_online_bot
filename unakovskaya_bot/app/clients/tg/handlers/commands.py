from aiogram.types import Message
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from unakovskaya_bot.variables import TG_BOT_USER_ADMIN
from unakovskaya_bot.static.texts import TEXTS
from unakovskaya_bot.app.clients.tg.router import router
from unakovskaya_bot.app.clients.tg.keyboards.userkb import get_admin_keyboard
from unakovskaya_bot.app.user_services import sync_user, is_user_admin, \
    unset_user_admin
from unakovskaya_bot.app.clients.tg.handlers.manage_admin import set_admin
from unakovskaya_bot.app.clients.tg.handlers.manage_links import get_links


@router.message(CommandStart(), StateFilter("*"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await sync_user(
        user_id=message.from_user.id,
        platform='tg',
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    print(message.model_dump_json(indent=4))
    await message.answer(TEXTS.get('text_welcome'))

    try:
        admin_id = int(TG_BOT_USER_ADMIN)
    except (ValueError, TypeError):
        admin_id = None

    if admin_id and admin_id == message.from_user.id:
        await set_admin(message)
    else:
        await unset_user_admin(message.from_user.id, platform='tg')
        await get_links(message)


@router.message(Command("admin"), StateFilter("*"))
async def admin_start(message: Message, state: FSMContext):
    await state.clear()
    # Проверяем актуальность админа из ENV
    try:
        admin_id = int(TG_BOT_USER_ADMIN)
    except (ValueError, TypeError):
        admin_id = None

    if admin_id != message.from_user.id:
        await unset_user_admin(message.from_user.id, platform='tg')

    if not await is_user_admin(message.from_user.id, platform='tg'):
        await message.answer(TEXTS.get('text_restrict_admin'))
        return

    await message.answer(
        TEXTS.get('text_admin_panel'), reply_markup=get_admin_keyboard())
