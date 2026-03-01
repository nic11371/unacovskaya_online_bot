from asgiref.sync import sync_to_async
from unakovskaya_bot.app.models import User


@sync_to_async
def sync_user(
        user_id, platform, username=None, first_name=None, last_name=None):
    """
    Создает или обновляет данные пользователя.
    platform: 'tg' или 'vk'
    """
    defaults = {
        'first_name': first_name or "",
        'last_name': last_name or "",
    }

    if platform == 'tg':
        defaults['username'] = username if username else str(user_id)
        user, _ = User.objects.update_or_create(
            tg_id=user_id,
            defaults=defaults
        )
    elif platform == 'vk':
        defaults['username'] = username if username else f"vk_{user_id}"
        user, _ = User.objects.update_or_create(
            vk_id=user_id,
            defaults=defaults
        )
    else:
        return None

    return user


@sync_to_async
def is_user_admin(user_id: int, platform: str) -> bool:
    """
    Проверяет права администратора.
    platform: 'tg' или 'vk'
    """
    if platform == 'tg':
        return User.objects.filter(tg_id=user_id, is_admin=True).exists()
    elif platform == 'vk':
        return User.objects.filter(vk_id=user_id, is_admin=True).exists()
    return False


@sync_to_async
def set_user_admin(user_id):
    User.objects.filter(tg_id=user_id).update(is_admin=True)


@sync_to_async
def unset_user_admin(user_id):
    User.objects.filter(tg_id=user_id).update(is_admin=False)


@sync_to_async
def get_all_tg_users():
    return list(User.objects.filter(
        tg_id__isnull=False).values_list('tg_id', flat=True))
