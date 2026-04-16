import logging
from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.fsm.context import FSMContext
from unakovskaya_bot.static.texts import TEXTS
from unakovskaya_bot.app.clients.tg.router import router
from unakovskaya_bot.tasks import broadcast_tg
from unakovskaya_bot.app.clients.tg.states.states import BroadcastState
from unakovskaya_bot.app.clients.tg.backend import get_all_tg_users

logger = logging.getLogger(__name__)


@router.callback_query(F.data == "admin_article")
async def start_article(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(TEXTS.get('text_admin_article'))
    await state.set_state(BroadcastState.waiting_for_message)
    await callback.answer()


@router.message(BroadcastState.waiting_for_message, ~F.text.startswith('/'))
async def process_broadcast(message: Message, state: FSMContext):
    users_ids = await get_all_tg_users()

    try:
        broadcast_tg.delay(
            user_ids=users_ids,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
            admin_chat_id=message.from_user.id
        )
        logger.info(TEXTS.get('log_tg_broadcast_started'), len(users_ids))
        await message.answer(
            f"{TEXTS.get('text_start_mailing')} {len(users_ids)}")
    except Exception as e:
        logger.error(TEXTS.get('log_tg_broadcast_fail_queue'), e)
        await message.answer(TEXTS.get('text_broadcast_error').format(error=e))

    await state.clear()
