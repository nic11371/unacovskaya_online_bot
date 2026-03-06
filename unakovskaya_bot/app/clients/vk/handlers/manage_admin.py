import asyncio
from vkbottle import GroupEventType
from vkbottle.bot import Message, MessageEvent
from vkbottle.dispatch.rules.base import PayloadRule
from unakovskaya_bot.static.texts import TEXTS
from unakovskaya_bot.app.clients.vk.labeler import chat_labeler
from unakovskaya_bot.app.clients.vk.states.states import AddLinkState, \
    BroadcastState
from unakovskaya_bot.app.videolinks_services import add_video_link, get_links
from unakovskaya_bot.app.user_services import get_all_tg_users, set_user_admin
from unakovskaya_bot.app.clients.vk.keyboards.userkb import \
    get_admin_keyboard, get_delete_links_keyboard


async def set_admin(message: Message):
    await set_user_admin(message.from_id, platform='vk')
    await message.answer(TEXTS.get('text_welcome_admin'))


@chat_labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({"cmd": "admin_article"}))
async def start_article(event: MessageEvent):
    await event.edit_message(TEXTS.get('text_admin_article'))
    await event.ctx_api.state_dispenser.set(
        event.peer_id, BroadcastState.WAITING_FOR_MESSAGE)


@chat_labeler.message(state=BroadcastState.WAITING_FOR_MESSAGE)
async def process_broadcast(message: Message):
    if message.text.startswith('/'):
        return

    users_ids = await get_all_tg_users()
    count = 0

    status_msg = await message.answer(
        f"{TEXTS.get('text_start_mailing')} {len(users_ids)}")

    for user_id in users_ids:
        if user_id == message.from_id:
            continue
        try:
            # Простая отправка текста. Для медиа нужна другая логика.
            await message.ctx_api.messages.send(
                peer_id=user_id, message=message.text, random_id=0)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass

    await message.ctx_api.messages.edit(
        peer_id=status_msg.peer_id,
        message_id=status_msg.id,
        message=f"{TEXTS.get(
            'text_finish_mailing')} {count} из {len(users_ids)}"
    )
    await message.ctx_api.state_dispenser.delete(message.peer_id)


@chat_labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({"cmd": "admin_add"}))
async def start_add_link(event: MessageEvent):
    await event.edit_message(TEXTS.get('text_title_step'))
    await event.ctx_api.state_dispenser.set(
        event.peer_id, AddLinkState.WAITING_FOR_TITLE)


@chat_labeler.message(state=AddLinkState.WAITING_FOR_TITLE)
async def process_title(message: Message):
    if message.text.startswith('/'):
        return

    await message.ctx_api.state_dispenser.set(
        message.peer_id,
        AddLinkState.WAITING_FOR_TEXT,
        title=message.text
    )
    await message.answer(TEXTS.get('text_description_step'))


@chat_labeler.message(state=AddLinkState.WAITING_FOR_TEXT)
async def process_text(message: Message):
    if message.text.startswith('/'):
        return

    state_data = await message.ctx_api.state_dispenser.get(message.peer_id)
    title = state_data.payload.get('title')

    await message.ctx_api.state_dispenser.set(
        message.peer_id,
        AddLinkState.WAITING_FOR_URL,
        title=title,
        text=message.text
    )
    await message.answer(TEXTS.get('text_link_step'))


@chat_labeler.message(state=AddLinkState.WAITING_FOR_URL)
async def process_url(message: Message):
    if message.text.startswith('/'): return
    if not message.text.startswith("http"):
        await message.answer(TEXTS.get('text_wrong_link'))
        return

    state_data = await message.ctx_api.state_dispenser.get(message.peer_id)
    data = state_data.payload

    new_order = await add_video_link(
        title=data['title'],
        text=data['text'],
        url=message.text
    )

    await message.answer(
        f"{TEXTS.get('text_link_added')} {new_order}",
        keyboard=get_admin_keyboard())
    await message.ctx_api.state_dispenser.delete(message.peer_id)


@chat_labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({"cmd": "admin_list"}))
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


@chat_labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, PayloadRule({"cmd": "admin_back"}))
async def admin_back(event: MessageEvent):
    await event.edit_message(
        TEXTS.get('text_admin_panel'), keyboard=get_admin_keyboard())
