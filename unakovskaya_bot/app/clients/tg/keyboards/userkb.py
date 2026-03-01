from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


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
            text="Написать анонс", callback_data="admin_article")],
        [InlineKeyboardButton(
            text="➕ Добавить ссылку", callback_data="admin_add")],
        [InlineKeyboardButton(
            text="📋 Список (Удалить)", callback_data="admin_list")]
    ])
