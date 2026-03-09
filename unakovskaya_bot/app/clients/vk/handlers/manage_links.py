import asyncio
from typing import Dict
from vkbottle.bot import Message, MessageEvent
from vkbottle import GroupEventType
from vkbottle.dispatch.rules.base import FuncRule, PayloadRule
from unakovskaya_bot.variables import DELAY_LINK
from unakovskaya_bot.static.texts import TEXTS
from unakovskaya_bot.app.videolinks_services import get_active_links, \
    delete_video_link
from unakovskaya_bot.app.clients.vk.labeler import chat_labeler
from unakovskaya_bot.app.clients.vk.keyboards.userkb import next_link_btn
from unakovskaya_bot.app.clients.vk.handlers.manage_admin import \
    show_links_list
from unakovskaya_bot.app.clients.vk.utils import answer_event


user_events: Dict[int, asyncio.Event] = {}


async def get_links(message: Message):
    links = await get_active_links()
    if not links:
        await message.answer(TEXTS.get('text_no_links'))
        return

    user_id = message.from_id

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
                    # В VK редактируем сообщение, убирая клавиатуру
                    await message.ctx_api.messages.edit(
                        peer_id=message.peer_id,
                        message_id=previous_msg,
                        keyboard='{"buttons":[],"inline":true}'
                    )
                except Exception:
                    pass

            # Добавляем кнопку "Далее", если это не последняя ссылка
            keyboard = None
            if i < len(links) - 1:
                keyboard = next_link_btn()

            text_part = f"{link.title}\n\n{link.message_text}\n\n{link.url}"
            # message.answer возвращает ID сообщения (int)
            previous_msg = await message.answer(
                text_part, keyboard=keyboard)
    finally:
        # Очищаем событие после завершения цикла
        if user_id in user_events:
            del user_events[user_id]


@chat_labeler.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"cmd": "skip_link_delay"}))
async def skip_delay_handler(event: MessageEvent):
    user_id = event.user_id

    # Если пользователь сейчас чего-то ждет, прерываем ожидание
    if user_id in user_events:
        user_events[user_id].set()

    # Сразу убираем кнопку, чтобы показать реакцию
    try:
        await event.edit_message(keyboard='{"buttons":[],"inline":true}')
    except Exception:
        pass

    await answer_event(event)


@chat_labeler.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    FuncRule(lambda e: e.payload.get("cmd") == "del_link"))
async def delete_link_handler(event: MessageEvent):
    link_id = event.payload.get("id")
    if await delete_video_link(link_id):
        await event.show_snackbar(TEXTS.get('text_removed_link'))
        # Обновляем список
        await show_links_list(event)
    else:
        await event.show_snackbar(TEXTS.get('text_error_removed'))
