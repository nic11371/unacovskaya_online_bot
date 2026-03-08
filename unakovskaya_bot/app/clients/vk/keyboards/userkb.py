from vkbottle import Keyboard, KeyboardButtonColor, Text, Callback
from unakovskaya_bot.static.texts import TEXTS


def start_btn():
    """Кнопка старт/приветствие"""
    keyboard = Keyboard(one_time=True, inline=False)
    # Используем .add() вместо .schema() для простоты и читаемости
    keyboard.add(
        Text(TEXTS.get('btn_start', 'Start'), payload={"cmd": "welcome_btn"}),
        color=KeyboardButtonColor.POSITIVE
    )
    return keyboard.get_json()


def get_admin_keyboard():
    """Главное меню админа (Inline)"""
    keyboard = Keyboard(inline=True)

    keyboard.add(
        Callback(TEXTS.get('text_btn_art'), payload={"cmd": "admin_article"}),
        color=KeyboardButtonColor.PRIMARY
    )
    keyboard.row()

    keyboard.add(
        Callback(TEXTS.get('text_btn_link'), payload={"cmd": "admin_add"}),
        color=KeyboardButtonColor.POSITIVE
    )
    keyboard.row()

    keyboard.add(
        Callback(TEXTS.get('text_btn_rem'), payload={"cmd": "admin_list"}),
        color=KeyboardButtonColor.NEGATIVE
    )

    return keyboard.get_json()


def admin_back_btn():
    """Кнопка назад"""
    keyboard = Keyboard(inline=True)
    keyboard.add(
        Callback(TEXTS.get('text_btn_back'), payload={"cmd": "admin_back"})
    )
    return keyboard.get_json()


def get_delete_links_keyboard(links):
    """
    Генерирует клавиатуру со списком ссылок для удаления.
    Заменяет функцию del_link из aiogram версии.
    """
    keyboard = Keyboard(inline=True)

    for link in links:
        label = f"🗑 {link.order}. {link.title}"[:40]
        keyboard.add(
            Callback(label, payload={"cmd": "del_link", "id": link.id}),
            color=KeyboardButtonColor.NEGATIVE
        )
        keyboard.row()

    keyboard.add(
        Callback(TEXTS.get('text_btn_back'), payload={"cmd": "admin_back"})
    )
    return keyboard.get_json()


def next_link_btn():
    """Кнопка Далее"""
    keyboard = Keyboard(inline=True)
    keyboard.add(
        Callback(
            TEXTS.get('text_btn_next'), payload={"cmd": "skip_link_delay"}),
        color=KeyboardButtonColor.POSITIVE
    )
    return keyboard.get_json()
