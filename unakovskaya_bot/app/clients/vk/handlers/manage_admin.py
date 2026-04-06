import logging
from vkbottle import GroupEventType
from vkbottle.bot import Message, MessageEvent
from vkbottle.dispatch.rules.base import PayloadRule, FuncRule
from unakovskaya_bot.static.texts import TEXTS
from unakovskaya_bot.app.clients.vk.labeler import chat_labeler
from unakovskaya_bot.app.clients.vk.states.states import AddLinkState
from unakovskaya_bot.app.videolinks_services import add_video_link, get_links
from unakovskaya_bot.app.user_services import set_user_admin
from unakovskaya_bot.app.clients.vk.keyboards.userkb import (
    get_admin_keyboard, get_delete_links_keyboard
)
from unakovskaya_bot.app.clients.vk.utils import answer_event

logger = logging.getLogger(__name__)


async def set_admin(message: Message):
    await set_user_admin(message.from_id, platform='vk')
    await message.answer(TEXTS.get('text_welcome_admin'))


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
        keyboard=keyboard_json)
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
        keyboard=keyboard_json)
    await answer_event(event)


@chat_labeler.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"cmd": "admin_back"}))
async def admin_back(event: MessageEvent):
    await event.edit_message(
        TEXTS.get('text_admin_panel'), keyboard=get_admin_keyboard())
    await answer_event(event)
