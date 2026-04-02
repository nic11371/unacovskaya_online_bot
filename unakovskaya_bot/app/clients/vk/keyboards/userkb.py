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
    keyboard.row()

    keyboard.add(
        Callback(TEXTS.get('text_btn_email_admin'),
                 payload={"cmd": "admin_list_emails"})
    )
    keyboard.row()

    keyboard.add(
        Callback(TEXTS.get('text_btn_email_step'),
                 payload={"cmd": "admin_email_step"})
    )
    keyboard.row()

    keyboard.add(
        Callback(TEXTS.get('text_btn_email_text'),
                 payload={"cmd": "admin_email_text"})
    )

    return keyboard.get_json()


def admin_back_btn():
    """Кнопка назад"""
    keyboard = Keyboard(inline=True)
    keyboard.add(
        Callback(TEXTS.get('text_btn_back'), payload={"cmd": "admin_back"})
    )
    return keyboard.get_json()


PAGE_SIZE = 4


def get_delete_links_keyboard(links, page=0):
    """
    Генерирует клавиатуру со списком ссылок для удаления (с пагинацией).
    VK ограничивает inline-клавиатуры до 6 строк.
    Максимум строк: 4 ссылки + 1 навигация + 1 «Назад» = 6.
    """
    keyboard = Keyboard(inline=True)

    start = page * PAGE_SIZE
    page_links = links[start:start + PAGE_SIZE]

    for i, link in enumerate(page_links):
        label = f"🗑 {link.order}. {link.title}"[:40]
        keyboard.add(
            Callback(label, payload={"cmd": "del_link", "id": link.id}),
            color=KeyboardButtonColor.NEGATIVE
        )
        if i < len(page_links) - 1:
            keyboard.row()

    has_prev = page > 0
    has_next = start + PAGE_SIZE < len(links)

    if has_prev or has_next:
        keyboard.row()
        if has_prev:
            keyboard.add(Callback(
                "◀", payload={"cmd": "admin_list_page", "page": page - 1}
            ))
        if has_next:
            keyboard.add(Callback(
                "▶", payload={"cmd": "admin_list_page", "page": page + 1}
            ))

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
