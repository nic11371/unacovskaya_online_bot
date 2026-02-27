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
