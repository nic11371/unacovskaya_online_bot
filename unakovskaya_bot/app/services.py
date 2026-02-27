from asgiref.sync import sync_to_async
from unakovskaya_bot.app.models import VideoLink


@sync_to_async
def get_formatted_links_text():
    """
    Получает активные ссылки из БД и формирует общий текст сообщения.
    """
    links = VideoLink.objects.filter(is_active=True).order_by('order')

    if not links.exists():
        return None

    text_parts = []
    for link in links:
        # Формат: "1. Название (ссылка)" или любой другой
        part = f"{link.order}. {link.title}\n{link.message_text}\n🔗 {link.url}"
        text_parts.append(part)

    return "\n\n".join(text_parts)
