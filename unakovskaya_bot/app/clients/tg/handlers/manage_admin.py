import asyncio
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram import F
from aiogram.fsm.context import FSMContext
from unakovskaya_bot.static.texts import TEXTS
from unakovskaya_bot.app.clients.tg.router import router
from unakovskaya_bot.app.clients.tg.states.states import AddLinkState, \
    BroadcastState
from unakovskaya_bot.app.videolinks_services import add_video_link, get_links
from unakovskaya_bot.app.user_services import get_all_tg_users, set_user_admin
from unakovskaya_bot.app.clients.tg.keyboards.userkb import \
    get_admin_keyboard, admin_back_btn, del_link


async def set_admin(message: Message):
    await set_user_admin(message.from_user.id, platform='tg')
    await message.answer(TEXTS.get('text_welcome_admin'))


@router.callback_query(F.data == "admin_article")
async def start_article(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(TEXTS.get('text_admin_article'))
    await state.set_state(BroadcastState.waiting_for_message)
    await callback.answer()


@router.message(BroadcastState.waiting_for_message, ~F.text.startswith('/'))
async def process_broadcast(message: Message, state: FSMContext):
    users_ids = await get_all_tg_users()
    count = 0

    status_msg = await message.answer(
        f"{TEXTS.get('text_start_mailing')} {len(users_ids)}")

    for user_id in users_ids:
        if user_id == message.from_user.id:
            continue
        try:
            await message.copy_to(chat_id=user_id)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass

    await status_msg.edit_text(
        f"{TEXTS.get('text_finish_mailing')} {count} из {len(users_ids)}")
    await state.clear()


@router.callback_query(F.data == "admin_add")
async def start_add_link(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(TEXTS.get('text_title_step'))
    await state.set_state(AddLinkState.waiting_for_title)
    await callback.answer()


@router.message(AddLinkState.waiting_for_title, ~F.text.startswith('/'))
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer(TEXTS.get('text_description_step'))
    await state.set_state(AddLinkState.waiting_for_text)


@router.message(AddLinkState.waiting_for_text, ~F.text.startswith('/'))
async def process_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer(TEXTS.get('text_link_step'))
    await state.set_state(AddLinkState.waiting_for_url)


@router.message(AddLinkState.waiting_for_url, ~F.text.startswith('/'))
async def process_url(message: Message, state: FSMContext):
    if not message.text.startswith("http"):
        await message.answer(TEXTS.get('text_wrong_link'))
        return

    data = await state.get_data()

    new_order = await add_video_link(
        title=data['title'],
        text=data['text'],
        url=message.text
    )

    await message.answer(
        f"{TEXTS.get('text_link_added')} {new_order}",
        reply_markup=get_admin_keyboard())
    await state.clear()


@router.callback_query(F.data == "admin_list")
async def show_links_list(callback: CallbackQuery):
    links = await get_links()

    if not links:
        await callback.answer(TEXTS.get('text_empty_list'), show_alert=True)
        return

    buttons = []
    for link in links:
        btn_text = f"🗑 {link.order}. {link.title}"
        buttons.append(del_link(btn_text, link))

    buttons.append(admin_back_btn())

    await callback.message.edit_text(
        TEXTS.get('text_btn_remove'),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    await callback.message.edit_text(
        TEXTS.get('text_admin_panel'), reply_markup=get_admin_keyboard())
