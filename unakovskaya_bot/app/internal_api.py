import json
import secrets

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from unakovskaya_bot.app.models import BotSetting, User, VideoLink
from unakovskaya_bot.static.texts import TEXTS
from unakovskaya_bot.variables import EMAIL_AFTER_STEP, INTERNAL_API_TOKEN


def _link_payload(link: VideoLink) -> dict:
    return {
        "id": link.id,
        "order": link.order,
        "title": link.title,
        "message_text": link.message_text,
        "url": link.url,
        "delay_minutes": link.delay_minutes,
        "is_active": link.is_active,
    }


def _unauthorized() -> JsonResponse:
    return JsonResponse({"detail": "Unauthorized"}, status=403)


def _misconfigured() -> JsonResponse:
    return JsonResponse({"detail": "INTERNAL_API_TOKEN is not configured"}, status=503)


def _authorize(request: HttpRequest) -> HttpResponse | None:
    if not INTERNAL_API_TOKEN:
        return _misconfigured()

    token = request.headers.get("X-Internal-Token", "")
    if not secrets.compare_digest(token, INTERNAL_API_TOKEN):
        return _unauthorized()

    return None


def _parse_json(request: HttpRequest) -> dict:
    if not request.body:
        return {}
    return json.loads(request.body.decode("utf-8"))


def _user_lookup(platform: str) -> str:
    if platform == "tg":
        return "tg_id"
    if platform == "vk":
        return "vk_id"
    raise ValueError("Unsupported platform")


@csrf_exempt
@require_http_methods(["POST"])
def users_sync(request: HttpRequest) -> JsonResponse:
    if auth_response := _authorize(request):
        return auth_response

    payload = _parse_json(request)
    platform = payload.get("platform")
    user_id = payload.get("user_id")

    if platform not in {"tg", "vk"} or user_id is None:
        return JsonResponse({"detail": "Invalid payload"}, status=400)

    defaults = {
        "first_name": payload.get("first_name") or "",
        "last_name": payload.get("last_name") or "",
        "username": payload.get("username") or "",
    }

    lookup_field = _user_lookup(platform)
    user, _ = User.objects.update_or_create(
        **{lookup_field: user_id},
        defaults=defaults,
    )
    return JsonResponse(
        {
            "id": user.id,
            "tg_id": user.tg_id,
            "vk_id": user.vk_id,
            "username": user.username,
        }
    )


@csrf_exempt
@require_http_methods(["GET"])
def user_is_admin(request: HttpRequest, platform: str, user_id: int) -> JsonResponse:
    if auth_response := _authorize(request):
        return auth_response

    lookup_field = _user_lookup(platform)
    is_admin = User.objects.filter(**{lookup_field: user_id}, is_admin=True).exists()
    return JsonResponse({"is_admin": is_admin})


@csrf_exempt
@require_http_methods(["POST"])
def user_set_admin(request: HttpRequest, platform: str, user_id: int) -> JsonResponse:
    if auth_response := _authorize(request):
        return auth_response

    lookup_field = _user_lookup(platform)
    User.objects.filter(**{lookup_field: user_id}).update(is_admin=True)
    return JsonResponse({"ok": True})


@csrf_exempt
@require_http_methods(["POST"])
def user_unset_admin(request: HttpRequest, platform: str, user_id: int) -> JsonResponse:
    if auth_response := _authorize(request):
        return auth_response

    lookup_field = _user_lookup(platform)
    User.objects.filter(**{lookup_field: user_id}).update(is_admin=False)
    return JsonResponse({"ok": True})


@csrf_exempt
@require_http_methods(["POST"])
def user_add_email(request: HttpRequest, platform: str, user_id: int) -> JsonResponse:
    if auth_response := _authorize(request):
        return auth_response

    payload = _parse_json(request)
    email = payload.get("email", "").strip()
    if not email:
        return JsonResponse({"detail": "Email is required"}, status=400)

    lookup_field = _user_lookup(platform)
    User.objects.filter(**{lookup_field: user_id}).update(email=email)
    return JsonResponse({"ok": True})


@csrf_exempt
@require_http_methods(["GET"])
def tg_user_ids(request: HttpRequest) -> JsonResponse:
    if auth_response := _authorize(request):
        return auth_response

    user_ids = list(User.objects.filter(tg_id__isnull=False).values_list("tg_id", flat=True))
    return JsonResponse({"user_ids": user_ids})


@csrf_exempt
@require_http_methods(["GET"])
def report_emails(request: HttpRequest) -> JsonResponse:
    if auth_response := _authorize(request):
        return auth_response

    emails = list(
        User.objects.exclude(email="")
        .values_list("email", flat=True)
        .order_by("created_at")
    )
    return JsonResponse({"emails": emails})


@csrf_exempt
@require_http_methods(["GET", "PUT"])
def email_step_view(request: HttpRequest) -> JsonResponse:
    if auth_response := _authorize(request):
        return auth_response

    if request.method == "GET":
        obj = BotSetting.objects.filter(key="email_after_step").first()
        value = int(obj.value) if obj else EMAIL_AFTER_STEP
        return JsonResponse({"value": value})

    payload = _parse_json(request)
    value = payload.get("value")
    try:
        step = int(value)
    except (TypeError, ValueError):
        return JsonResponse({"detail": "Invalid step"}, status=400)

    BotSetting.objects.update_or_create(
        key="email_after_step",
        defaults={"value": str(step)},
    )
    return JsonResponse({"ok": True, "value": step})


@csrf_exempt
@require_http_methods(["GET", "PUT"])
def email_text_view(request: HttpRequest) -> JsonResponse:
    if auth_response := _authorize(request):
        return auth_response

    if request.method == "GET":
        obj = BotSetting.objects.filter(key="email_ask_text").first()
        value = obj.value if obj else TEXTS.get("text_ask_email")
        return JsonResponse({"value": value})

    payload = _parse_json(request)
    value = str(payload.get("value", "")).strip()
    if not value:
        return JsonResponse({"detail": "Text is required"}, status=400)

    BotSetting.objects.update_or_create(
        key="email_ask_text",
        defaults={"value": value},
    )
    return JsonResponse({"ok": True, "value": value})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def links_view(request: HttpRequest) -> JsonResponse:
    if auth_response := _authorize(request):
        return auth_response

    if request.method == "GET":
        links = [_link_payload(link) for link in VideoLink.objects.all().order_by("order")]
        return JsonResponse({"links": links})

    payload = _parse_json(request)
    title = str(payload.get("title", "")).strip()
    message_text = str(payload.get("message_text", "")).strip()
    url = str(payload.get("url", "")).strip()

    if not title or not message_text or not url:
        return JsonResponse({"detail": "title, message_text and url are required"}, status=400)

    last_link = VideoLink.objects.order_by("-order").first()
    next_order = 1 if last_link is None else last_link.order + 1

    link = VideoLink.objects.create(
        order=next_order,
        title=title,
        message_text=message_text,
        url=url,
        is_active=True,
    )
    return JsonResponse({"id": link.id, "order": link.order})


@csrf_exempt
@require_http_methods(["GET"])
def active_links_view(request: HttpRequest) -> JsonResponse:
    if auth_response := _authorize(request):
        return auth_response

    links = [
        _link_payload(link)
        for link in VideoLink.objects.filter(is_active=True).order_by("order")
    ]
    return JsonResponse({"links": links})


@csrf_exempt
@require_http_methods(["DELETE"])
def links_delete(request: HttpRequest, link_id: int) -> JsonResponse:
    if auth_response := _authorize(request):
        return auth_response

    deleted_count, _ = VideoLink.objects.filter(id=link_id).delete()
    return JsonResponse({"deleted": deleted_count > 0})
