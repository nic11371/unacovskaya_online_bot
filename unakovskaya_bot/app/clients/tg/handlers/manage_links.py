import re
import asyncio
from typing import Dict
from aiogram.types import Message, CallbackQuery
from aiogram import F
from unakovskaya_bot.variables import DELAY_LINK, EMAIL_TIMEOUT
from unakovskaya_bot.static.texts import TEXTS
from unakovskaya_bot.app.videolinks_services import get_active_links, \
    delete_video_link
from unakovskaya_bot.app.user_services import add_email, get_email_step
from unakovskaya_bot.app.clients.tg.router import router
from unakovskaya_bot.app.clients.tg.keyboards.userkb import next_link_btn
from unakovskaya_bot.app.clients.tg.handlers.manage_admin import \
    show_links_list


user_events: Dict[int, asyncio.Event] = {}
user_email_futures: Dict[int, asyncio.Future] = {}
user_skip_delay: set = set()


async def get_links(message: Message):
    links = await get_active_links()
    if not links:
        await message.answer(TEXTS.get('text_no_links'))
        return

    user_id = message.from_user.id

    if user_id in user_events:
        return

    user_events[user_id] = asyncio.Event()
    previous_msg = None
    email_step = await get_email_step()

    try:
        for i, link in enumerate(links):
            if i > 0:
                if user_id in user_skip_delay:
                    user_skip_delay.discard(user_id)
                else:
                    user_events[user_id].clear()
                    try:
                        await asyncio.wait_for(
                            user_events[user_id].wait(), timeout=DELAY_LINK)
                    except asyncio.TimeoutError:
                        pass

            if previous_msg:
                try:
                    await previous_msg.edit_reply_markup(reply_markup=None)
                except Exception:
                    pass

            keyboard = None
            if i < len(links) - 1:
                keyboard = next_link_btn()

            text_part = f"{link.title}\n\n{link.url}\n\n{link.message_text}"
            previous_msg = await message.answer(
                text_part, reply_markup=keyboard)

            # После нужного шага — запрашиваем email
            if link.order == email_step:
                if previous_msg:
                    try:
                        await previous_msg.edit_reply_markup(reply_markup=None)
                    except Exception:
                        pass
                await message.answer(TEXTS.get('text_ask_email'))
                loop = asyncio.get_running_loop()
                future = loop.create_future()
                user_email_futures[user_id] = future
                try:
                    email = await asyncio.wait_for(
                        asyncio.shield(future), timeout=EMAIL_TIMEOUT)
                    await add_email(user_id, email, 'tg')
                    await message.answer(TEXTS.get('text_email_saved'))
                except asyncio.TimeoutError:
                    await message.answer(TEXTS.get('text_email_timeout'))
                finally:
                    user_email_futures.pop(user_id, None)
                user_skip_delay.add(user_id)
                previous_msg = None
    finally:
        if user_id in user_events:
            del user_events[user_id]


@router.message(lambda m: m.from_user and m.from_user.id in user_email_futures)
async def email_input_handler(message: Message):
    user_id = message.from_user.id
    email = message.text.strip() if message.text else ""

    if re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        future = user_email_futures.get(user_id)
        if future and not future.done():
            future.set_result(email)
    else:
        await message.answer(TEXTS.get('text_email_invalid'))


@router.callback_query(F.data == "skip_link_delay")
async def skip_delay_handler(callback: CallbackQuery):
    user_id = callback.from_user.id

    if user_id in user_events:
        user_events[user_id].set()

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()


@router.callback_query(F.data.startswith("del_link_"))
async def delete_link_handler(callback: CallbackQuery):
    link_id = int(callback.data.split("_")[-1])
    if await delete_video_link(link_id):
        await callback.answer(TEXTS.get('text_removed_link'))
        await show_links_list(callback)
    else:
        await callback.answer(TEXTS.get('text_error_removed'), show_alert=True)
