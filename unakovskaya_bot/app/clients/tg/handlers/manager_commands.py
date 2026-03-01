import asyncio
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from unakovskaya_bot.app.clients.tg.router import router
from unakovskaya_bot.app.clients.tg.states.states import AddLinkState, \
    BroadcastState
from unakovskaya_bot.app.videolinks_services import add_video_link, \
    delete_video_link, get_links
from unakovskaya_bot.app.user_services import is_user_admin, get_all_tg_users
from unakovskaya_bot.app.clients.tg.keyboards.userkb import get_admin_keyboard


@router.message(Command("admin"))
async def admin_start(message: Message):
    if not await is_user_admin(message.from_user.id, platform='tg'):
        await message.answer("⛔️ У вас нет прав администратора.")
        return

    await message.answer(
        "🔧 Панель администратора:", reply_markup=get_admin_keyboard())


@router.callback_query(F.data == "admin_article")
async def start_article(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Отправьте сообщение (текст, фото, видео, голосовое) для всех.\n\n"
        "💡 <b>Лайфхак:</b> Вы можете использовать «Отложенную отправку» "
        "(зажать кнопку отправки), чтобы запланировать рассылку на будущее.")
    await state.set_state(BroadcastState.waiting_for_message)
    await callback.answer()


@router.message(BroadcastState.waiting_for_message)
async def process_broadcast(message: Message, state: FSMContext):
    users_ids = await get_all_tg_users()
    count = 0

    status_msg = await message.answer(
        f"Начинаю рассылку на {len(users_ids)} пользователей...")

    for user_id in users_ids:
        if user_id == message.from_user.id:
            continue
        try:
            await message.copy_to(chat_id=user_id)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass

    await status_msg.edit_text(
        f"Рассылка завершена. Успешно отправлено: {count} из {len(users_ids)}")
    await state.clear()


@router.callback_query(F.data == "admin_add")
async def start_add_link(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название шага (Title):")
    await state.set_state(AddLinkState.waiting_for_title)
    await callback.answer()


@router.message(AddLinkState.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите текст описания:")
    await state.set_state(AddLinkState.waiting_for_text)


@router.message(AddLinkState.waiting_for_text)
async def process_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("Введите ссылку (URL):")
    await state.set_state(AddLinkState.waiting_for_url)


@router.message(AddLinkState.waiting_for_url)
async def process_url(message: Message, state: FSMContext):
    if not message.text.startswith("http"):
        await message.answer(
            "❌ Ссылка должна начинаться с http. Попробуйте снова.")
        return

    data = await state.get_data()

    new_order = await add_video_link(
        title=data['title'],
        text=data['text'],
        url=message.text
    )

    await message.answer(
        f"✅ Ссылка добавлена! Номер шага: {new_order}",
        reply_markup=get_admin_keyboard())
    await state.clear()


@router.callback_query(F.data == "admin_list")
async def show_links_list(callback: CallbackQuery):
    links = await get_links()

    if not links:
        await callback.answer("Список пуст", show_alert=True)
        return

    buttons = []
    for link in links:
        btn_text = f"🗑 {link.order}. {link.title}"
        buttons.append([InlineKeyboardButton(
            text=btn_text, callback_data=f"del_link_{link.id}")])

    buttons.append([InlineKeyboardButton(
        text="🔙 Назад", callback_data="admin_back")])

    await callback.message.edit_text(
        "Нажмите на пункт, чтобы УДАЛИТЬ его:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("del_link_"))
async def delete_link_handler(callback: CallbackQuery):
    link_id = int(callback.data.split("_")[-1])
    if await delete_video_link(link_id):
        await callback.answer("✅ Удалено")
        # Обновляем список
        await show_links_list(callback)
    else:
        await callback.answer("❌ Ошибка удаления", show_alert=True)


@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔧 Панель администратора:", reply_markup=get_admin_keyboard())
