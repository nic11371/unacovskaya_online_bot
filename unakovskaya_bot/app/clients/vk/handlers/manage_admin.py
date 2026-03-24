import asyncio
import aiohttp
from vkbottle import GroupEventType
from vkbottle.bot import Message, MessageEvent
from vkbottle.dispatch.rules.base import PayloadRule, FuncRule
from unakovskaya_bot.static.texts import TEXTS
from unakovskaya_bot.variables import DELAY_VK_MAIL
from unakovskaya_bot.app.clients.vk.labeler import chat_labeler
from unakovskaya_bot.app.clients.vk.states.states import AddLinkState, \
    BroadcastState, EmailStepState
from unakovskaya_bot.app.videolinks_services import add_video_link, get_links
from unakovskaya_bot.app.user_services import get_all_vk_users, set_user_admin, \
    get_user_emails, get_email_step, set_email_step
from unakovskaya_bot.app.clients.vk.keyboards.userkb import \
    get_admin_keyboard, get_delete_links_keyboard
from unakovskaya_bot.app.clients.vk.utils import answer_event


async def set_admin(message: Message):
    await set_user_admin(message.from_id, platform='vk')
    await message.answer(TEXTS.get('text_welcome_admin'))


@chat_labeler.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"cmd": "admin_article"}))
async def start_article(event: MessageEvent):
    await event.edit_message(TEXTS.get('text_admin_article'))
    await event.ctx_api.state_dispenser.set(
        event.peer_id, BroadcastState.WAITING_FOR_MESSAGE)

    await answer_event(event)


@chat_labeler.message(state=BroadcastState.WAITING_FOR_MESSAGE)
async def process_broadcast(message: Message):
    if message.text.startswith('/'):
        return

    users_ids = await get_all_vk_users()
    count = 0

    status_msg = await message.answer(
        f"{TEXTS.get('text_start_mailing')} {len(users_ids)}")

    # Собираем вложения (фото, видео, документы) в строку для отправки
    attachments = []
    if message.attachments:
        for attachment in message.attachments:
            media = attachment.photo or \
                attachment.video or \
                attachment.doc or \
                attachment.audio
            if media:
                # Определяем тип вложения
                type_str = ""
                if attachment.photo:
                    type_str = "photo"
                elif attachment.video:
                    type_str = "video"
                elif attachment.doc:
                    type_str = "doc"
                elif attachment.audio:
                    type_str = "audio"

                if type_str:
                    # Формат: type{owner_id}_{id}_{access_key}
                    att_str = f"{type_str}{media.owner_id}_{media.id}"
                    if getattr(media, "access_key", None):
                        att_str += f"_{media.access_key}"
                    attachments.append(att_str)

    attachment_str = ",".join(attachments) if attachments else None

    for user_id in users_ids:
        if user_id == message.from_id:
            continue
        try:
            await message.ctx_api.messages.send(
                peer_id=user_id,
                message=message.text,
                attachment=attachment_str,
                random_id=0
            )
            count += 1
            await asyncio.sleep(DELAY_VK_MAIL)
        except Exception:
            pass

    await message.ctx_api.messages.edit(
        peer_id=status_msg.peer_id,
        message_id=status_msg.message_id,
        message=f"{TEXTS.get(
            'text_finish_mailing')} {count} из {len(users_ids)}"
    )
    await message.ctx_api.state_dispenser.delete(message.peer_id)


@chat_labeler.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"cmd": "admin_add"}))
async def start_add_link(event: MessageEvent):
    await event.edit_message(TEXTS.get('text_title_step'))
    await event.ctx_api.state_dispenser.set(
        event.peer_id, AddLinkState.WAITING_FOR_TITLE)

    await answer_event(event)


@chat_labeler.message(state=AddLinkState.WAITING_FOR_TITLE)
async def process_title(message: Message):
    if message.text.startswith('/'):
        return

    await message.ctx_api.state_dispenser.set(
        message.peer_id,
        AddLinkState.WAITING_FOR_URL,
        title=message.text
    )
    await message.answer(TEXTS.get('text_link_step'))


@chat_labeler.message(state=AddLinkState.WAITING_FOR_URL)
async def process_url(message: Message):
    if message.text.startswith('/'):
        return
    if not message.text.startswith("http"):
        await message.answer(TEXTS.get('text_wrong_link'))
        return

    state_data = await message.ctx_api.state_dispenser.get(message.peer_id)
    title = state_data.payload.get('title')

    await message.ctx_api.state_dispenser.set(
        message.peer_id,
        AddLinkState.WAITING_FOR_TEXT,
        title=title,
        url=message.text
    )
    await message.answer(TEXTS.get('text_description_step'))


@chat_labeler.message(state=AddLinkState.WAITING_FOR_TEXT)
async def process_text(message: Message):
    if message.text.startswith('/'):
        return

    state_data = await message.ctx_api.state_dispenser.get(message.peer_id)
    data = state_data.payload

    new_order = await add_video_link(
        title=data['title'],
        text=message.text,
        url=data['url']
    )

    await message.answer(
        f"{TEXTS.get('text_link_added')} {new_order}",
        keyboard=get_admin_keyboard())
    await message.ctx_api.state_dispenser.delete(message.peer_id)


@chat_labeler.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"cmd": "admin_list"}))
async def show_links_list(event: MessageEvent):
    links = await get_links()

    if not links:
        await event.show_snackbar(TEXTS.get('text_empty_list'))
        return

    keyboard_json = get_delete_links_keyboard(links)
    await event.edit_message(
        TEXTS.get('text_btn_remove'),
        keyboard=keyboard_json
    )

    await answer_event(event)


@chat_labeler.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    FuncRule(lambda e: e.payload.get("cmd") == "admin_list_page"))
async def show_links_list_page(event: MessageEvent):
    page = event.payload.get("page", 0)
    links = await get_links()

    if not links:
        await event.show_snackbar(TEXTS.get('text_empty_list'))
        return

    keyboard_json = get_delete_links_keyboard(links, page=page)
    await event.edit_message(
        TEXTS.get('text_btn_remove'),
        keyboard=keyboard_json
    )

    await answer_event(event)


@chat_labeler.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"cmd": "admin_back"}))
async def admin_back(event: MessageEvent):
    await event.edit_message(
        TEXTS.get('text_admin_panel'), keyboard=get_admin_keyboard())

    await answer_event(event)


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
            message=f"📧 Emails: {len(emails)}",
            random_id=0
        )
    except Exception as e:
        await event.ctx_api.messages.send(
            peer_id=peer_id,
            message=f"❌ Ошибка при отправке файла: {e}",
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
