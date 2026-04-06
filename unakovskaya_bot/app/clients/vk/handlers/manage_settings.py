import logging
import aiohttp
from vkbottle import GroupEventType
from vkbottle.bot import Message, MessageEvent
from vkbottle.dispatch.rules.base import PayloadRule
from unakovskaya_bot.static.texts import TEXTS
from unakovskaya_bot.app.clients.vk.labeler import chat_labeler
from unakovskaya_bot.app.clients.vk.states.states import EmailStepState, \
    EmailTextState
from unakovskaya_bot.app.clients.vk.keyboards.userkb import get_admin_keyboard
from unakovskaya_bot.app.clients.vk.utils import answer_event
from unakovskaya_bot.app.user_services import (
    get_user_emails,
    get_email_step,
    set_email_step,
    get_email_text,
    set_email_text
)

logger = logging.getLogger(__name__)


@chat_labeler.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"cmd": "admin_list_emails"}))
async def send_emails_file(event: MessageEvent):
    emails = await get_user_emails()

    if not emails:
        await event.show_snackbar(TEXTS.get('text_empty_list_emails'))
        return

    content = "\n".join(emails).encode('utf-8')
    peer_id = event.peer_id

    try:
        upload_server = await event.ctx_api.docs.get_messages_upload_server(
            peer_id=peer_id, type="doc")
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field('file', content,
                           filename='emails.txt',
                           content_type='text/plain')
            async with session.post(
                    upload_server.upload_url, data=form) as resp:
                result = await resp.json()

        saved = await event.ctx_api.docs.save(
            file=result['file'], title='emails.txt')
        doc = saved.doc
        attachment = f"doc{doc.owner_id}_{doc.id}"

        await event.ctx_api.messages.send(
            peer_id=peer_id,
            attachment=attachment,
            message=TEXTS.get('text_emails_caption').format(count=len(emails)),
            random_id=0
        )
    except Exception as e:
        await event.ctx_api.messages.send(
            peer_id=peer_id,
            message=TEXTS.get('text_emails_send_error').format(error=e),
            random_id=0
        )

    await answer_event(event)


@chat_labeler.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"cmd": "admin_email_step"}))
async def ask_email_step(event: MessageEvent):
    current = await get_email_step()
    await event.ctx_api.messages.send(
        peer_id=event.peer_id,
        message=TEXTS.get('text_ask_email_step').format(current),
        random_id=0
    )
    await event.ctx_api.state_dispenser.set(
        event.peer_id, EmailStepState.WAITING_FOR_STEP)
    await answer_event(event)


@chat_labeler.message(state=EmailStepState.WAITING_FOR_STEP)
async def process_email_step(message: Message):
    if message.text.startswith('/'):
        return

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
        keyboard=get_admin_keyboard())
    await message.ctx_api.state_dispenser.delete(message.peer_id)


@chat_labeler.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"cmd": "admin_email_text"}))
async def ask_email_text(event: MessageEvent):
    current = await get_email_text()
    await event.ctx_api.messages.send(
        peer_id=event.peer_id,
        message=TEXTS.get('text_ask_email_text').format(current),
        random_id=0
    )
    await event.ctx_api.state_dispenser.set(
        event.peer_id, EmailTextState.WAITING_FOR_TEXT)
    await answer_event(event)


@chat_labeler.message(state=EmailTextState.WAITING_FOR_TEXT)
async def process_email_text(message: Message):
    if message.text.startswith('/'):
        return

    await set_email_text(message.text.strip())
    await message.answer(
        TEXTS.get('text_email_text_saved'),
        keyboard=get_admin_keyboard())
    await message.ctx_api.state_dispenser.delete(message.peer_id)
