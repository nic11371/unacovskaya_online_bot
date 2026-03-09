import asyncio
from typing import Dict
from aiogram.types import Message, CallbackQuery
from aiogram import F
from unakovskaya_bot.variables import DELAY_LINK
from unakovskaya_bot.static.texts import TEXTS
from unakovskaya_bot.app.videolinks_services import get_active_links, \
    delete_video_link
from unakovskaya_bot.app.clients.tg.router import router
from unakovskaya_bot.app.clients.tg.keyboards.userkb import next_link_btn
from unakovskaya_bot.app.clients.tg.handlers.manage_admin import \
    show_links_list


# Словарь для хранения событий ожидания (asyncio.Event) для каждого пользователя Telegram.
user_events: Dict[int, asyncio.Event] = {}


async def get_links(message: Message):
    links = await get_active_links()
    if not links:
        await message.answer(TEXTS.get('text_no_links'))
        return

    user_id = message.from_user.id
    
    if user_id in user_events:
        # Если просмотр уже идет, не запускаем второй поток
        return

    # Создаем событие для управления ожиданием
    user_events[user_id] = asyncio.Event()

    previous_msg = None

    try:
        for i, link in enumerate(links):
            # Делаем задержку только если это не первая ссылка
            if i > 0:
                user_events[user_id].clear()
                try:
                    # Ждем либо таймаут, либо событие (нажатие кнопки)
                    await asyncio.wait_for(
                        user_events[user_id].wait(), timeout=DELAY_LINK)
                except asyncio.TimeoutError:
                    pass

            # Убираем кнопку у предыдущего сообщения
            if previous_msg:
                try:
                    await previous_msg.edit_reply_markup(reply_markup=None)
                except Exception:
                    pass

            # Добавляем кнопку "Далее", если это не последняя ссылка
            keyboard = None
            if i < len(links) - 1:
                keyboard = next_link_btn()

            text_part = f"{link.title}\n\n{link.message_text}\n\n{link.url}"
            previous_msg = await message.answer(
                text_part, reply_markup=keyboard)
    finally:
        # Очищаем событие после завершения цикла
        if user_id in user_events:
            del user_events[user_id]


@router.callback_query(F.data == "skip_link_delay")
async def skip_delay_handler(callback: CallbackQuery):
    user_id = callback.from_user.id

    # Если пользователь сейчас чего-то ждет, прерываем ожидание
    if user_id in user_events:
        user_events[user_id].set()

    # Сразу убираем кнопку, чтобы показать реакцию
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()


@router.callback_query(F.data.startswith("del_link_"))
async def delete_link_handler(callback: CallbackQuery):
    link_id = int(callback.data.split("_")[-1])
    if await delete_video_link(link_id):
        await callback.answer(TEXTS.get('text_removed_link'))
        # Обновляем список
        await show_links_list(callback)
    else:
        await callback.answer(TEXTS.get('text_error_removed'), show_alert=True)
