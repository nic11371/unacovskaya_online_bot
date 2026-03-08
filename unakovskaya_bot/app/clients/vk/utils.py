from vkbottle.bot import MessageEvent


async def answer_event(event: MessageEvent):
    """
    Отправляет пустой ответ на событие (нажатие кнопки),
    чтобы убрать анимацию загрузки.
    """
    try:
        await event.ctx_api.messages.send_message_event_answer(
            event_id=event.event_id,
            user_id=event.user_id,
            peer_id=event.peer_id
        )
    except Exception:
        pass
