import logging
from vkbottle import GroupEventType
from vkbottle.bot import Message, MessageEvent
from vkbottle.dispatch.rules.base import PayloadRule
from unakovskaya_bot.static.texts import TEXTS
import unakovskaya_bot.app.clients.vk.labeler as vk_labeler
from unakovskaya_bot.app.clients.vk.labeler import chat_labeler
from unakovskaya_bot.app.clients.vk.states.states import BroadcastState
from unakovskaya_bot.app.clients.vk.utils import answer_event
from unakovskaya_bot.app.user_services import get_all_vk_users
from unakovskaya_bot.tasks import broadcast_vk

logger = logging.getLogger(__name__)


@chat_labeler.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"cmd": "admin_article"}))
async def start_article(event: MessageEvent):
    await event.edit_message(TEXTS.get('text_admin_article'))
    await vk_labeler.state_dispenser.set(
        event.peer_id, BroadcastState.WAITING_FOR_MESSAGE)
    await answer_event(event)


@chat_labeler.message(state=BroadcastState.WAITING_FOR_MESSAGE)
async def process_broadcast(message: Message):
    if message.text.startswith('/'):
        return

    users_ids = await get_all_vk_users()

    attachments = []
    if message.attachments:
        for attachment in message.attachments:
            media = (attachment.photo or attachment.video
                     or attachment.doc or attachment.audio)
            if media:
                if attachment.photo:
                    type_str = "photo"
                elif attachment.video:
                    type_str = "video"
                elif attachment.doc:
                    type_str = "doc"
                else:
                    type_str = "audio"

                att_str = f"{type_str}{media.owner_id}_{media.id}"
                if getattr(media, "access_key", None):
                    att_str += f"_{media.access_key}"
                attachments.append(att_str)

    attachment_str = ",".join(attachments) if attachments else None

    try:
        broadcast_vk.delay(
            user_ids=users_ids,
            text=message.text,
            attachment_str=attachment_str,
            from_user_id=message.from_id,
            admin_peer_id=message.peer_id
        )
        logger.info(TEXTS.get('log_vk_broadcast_started'), len(users_ids))
        await message.answer(
            f"{TEXTS.get('text_start_mailing')} {len(users_ids)}")
    except Exception as e:
        logger.error(TEXTS.get('log_vk_broadcast_fail_queue'), e)
        await message.answer(TEXTS.get('text_broadcast_error').format(error=e))

    await vk_labeler.state_dispenser.delete(message.peer_id)
