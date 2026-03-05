from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from unakovskaya_bot.static.texts import TEXTS


def start_btn():
    btn = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="welcome_btn",
                callback_data="welcome_btn")]
        ]
    )
    return btn


def get_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=TEXTS.get('text_btn_art'),
            callback_data="admin_article")],
        [InlineKeyboardButton(
            text=TEXTS.get('text_btn_link'),
            callback_data="admin_add")],
        [InlineKeyboardButton(
            text=TEXTS.get('text_btn_rem'),
            callback_data="admin_list")]
    ])


def admin_back_btn():
    return [InlineKeyboardButton(
        text=TEXTS.get('text_btn_back'),
        callback_data="admin_back")]


def del_link(btn_text, link):
    return [InlineKeyboardButton(
            text=btn_text,
            callback_data=f"del_link_{link.id}")]


def next_link_btn():
    return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=TEXTS.get('text_btn_next'),
                callback_data="skip_link_delay")]
        ])


def get_emails():
    return InlineKeyboardButton(inline_keyboard=[
        [InlineKeyboardButton(
            text=TEXTS.get('text_get_email'),
            callback_data="get_emails")]
    ])
