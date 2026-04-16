import logging
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram import F
from aiogram.fsm.context import FSMContext
from unakovskaya_bot.static.texts import TEXTS
from unakovskaya_bot.app.clients.tg.router import router
from unakovskaya_bot.app.clients.tg.states.states import EmailStepState, \
    EmailTextState
from unakovskaya_bot.app.clients.tg.backend import (
    get_user_emails,
    get_email_step,
    set_email_step,
    get_email_text,
    set_email_text
)
from unakovskaya_bot.app.clients.tg.keyboards.userkb import get_admin_keyboard

logger = logging.getLogger(__name__)


@router.callback_query(F.data == "admin_list_emails")
async def send_emails_file(callback: CallbackQuery):
    emails = await get_user_emails()

    if not emails:
        await callback.answer(
            TEXTS.get('text_empty_list_emails'), show_alert=True)
        return

    content = "\n".join(emails).encode('utf-8')
    file = BufferedInputFile(content, filename="emails.txt")
    await callback.message.answer_document(
        file,
        caption=TEXTS.get('text_emails_caption').format(count=len(emails)))
    await callback.answer()


@router.callback_query(F.data == "admin_email_step")
async def ask_email_step(callback: CallbackQuery, state: FSMContext):
    current = await get_email_step()
    await callback.message.answer(
        TEXTS.get('text_ask_email_step').format(current))
    await state.set_state(EmailStepState.waiting_for_step)
    await callback.answer()


@router.message(EmailStepState.waiting_for_step, ~F.text.startswith('/'))
async def process_email_step(message: Message, state: FSMContext):
    try:
        step = int(message.text.strip())
        if step < 1:
            raise ValueError
    except ValueError:
        await message.answer(TEXTS.get('text_email_step_invalid'))
        return

    await set_email_step(step)
    await message.answer(
        TEXTS.get('text_email_step_saved').format(step),
        reply_markup=get_admin_keyboard())
    await state.clear()


@router.callback_query(F.data == "admin_email_text")
async def ask_email_text(callback: CallbackQuery, state: FSMContext):
    current = await get_email_text()
    await callback.message.answer(
        TEXTS.get('text_ask_email_text').format(current))
    await state.set_state(EmailTextState.waiting_for_text)
    await callback.answer()


@router.message(EmailTextState.waiting_for_text, ~F.text.startswith('/'))
async def process_email_text(message: Message, state: FSMContext):
    await set_email_text(message.text.strip())
    await message.answer(
        TEXTS.get('text_email_text_saved'),
        reply_markup=get_admin_keyboard())
    await state.clear()
