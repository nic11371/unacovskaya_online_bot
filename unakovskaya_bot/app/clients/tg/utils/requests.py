from asgiref.sync import sync_to_async
from unakovskaya_bot.app.models import User


@sync_to_async
def get_user(tg_id):
    return User.objects.filter(tg_id=tg_id).first()


@sync_to_async
def set_user(tg_id):
    default_username = str(tg_id)
    user, created = User.objects.get_or_create(
        tg_id=tg_id,
        defaults={'username': default_username})
    return user


@sync_to_async
def save_info_user(
        tg_id,
        username=None,
        first_name=None,
        last_name=None
        ):

    User.objects.filter(tg_id=tg_id).update(
        username=username if username else str(tg_id),
        first_name=first_name or "",
        last_name=last_name or ""
    )
