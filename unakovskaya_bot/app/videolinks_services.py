from asgiref.sync import sync_to_async
from django.db.models import Max
from unakovskaya_bot.app.models import VideoLink


@sync_to_async
def get_links():
    return list(VideoLink.objects.all())


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
        part = f"{link.order}. {link.title}\n{link.message_text}\n {link.url}"
        text_parts.append(part)

    return "\n\n".join(text_parts)


@sync_to_async
def add_video_link(title, text, url):
    max_order = VideoLink.objects.aggregate(Max('order'))['order__max']
    next_order = 1 if max_order is None else max_order + 1

    VideoLink.objects.create(
        order=next_order,
        title=title,
        message_text=text,
        url=url,
        is_active=True
    )
    return next_order


@sync_to_async
def delete_video_link(link_id):
    deleted_count, _ = VideoLink.objects.filter(id=link_id).delete()
    return deleted_count > 0


@sync_to_async
def get_active_links():
    return list(VideoLink.objects.filter(is_active=True).order_by('order'))
