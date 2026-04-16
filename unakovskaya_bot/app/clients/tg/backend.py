import aiohttp
from dataclasses import dataclass
from typing import Any

from unakovskaya_bot.app.user_services import (
    add_email as local_add_email,
    get_all_tg_users as local_get_all_tg_users,
    get_email_step as local_get_email_step,
    get_email_text as local_get_email_text,
    get_user_emails as local_get_user_emails,
    is_user_admin as local_is_user_admin,
    set_email_step as local_set_email_step,
    set_email_text as local_set_email_text,
    set_user_admin as local_set_user_admin,
    sync_user as local_sync_user,
    unset_user_admin as local_unset_user_admin,
)
from unakovskaya_bot.app.videolinks_services import (
    add_video_link as local_add_video_link,
    delete_video_link as local_delete_video_link,
    get_active_links as local_get_active_links,
    get_links as local_get_links,
)
from unakovskaya_bot.variables import APP_API_BASE_URL, APP_API_TIMEOUT, APP_API_TOKEN


@dataclass(slots=True)
class VideoLinkDTO:
    id: int
    order: int
    title: str
    message_text: str
    url: str
    delay_minutes: int = 0
    is_active: bool = True


def _use_remote_api() -> bool:
    return bool(APP_API_BASE_URL)


def _serialize_link(link: Any) -> VideoLinkDTO:
    return VideoLinkDTO(
        id=link.id,
        order=link.order,
        title=link.title,
        message_text=link.message_text,
        url=link.url,
        delay_minutes=getattr(link, "delay_minutes", 0),
        is_active=getattr(link, "is_active", True),
    )


def _link_from_dict(payload: dict[str, Any]) -> VideoLinkDTO:
    return VideoLinkDTO(
        id=int(payload["id"]),
        order=int(payload["order"]),
        title=str(payload["title"]),
        message_text=str(payload["message_text"]),
        url=str(payload["url"]),
        delay_minutes=int(payload.get("delay_minutes", 0)),
        is_active=bool(payload.get("is_active", True)),
    )


async def _request(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    if not APP_API_BASE_URL:
        raise RuntimeError("APP_API_BASE_URL is not configured")

    headers = {}
    if APP_API_TOKEN:
        headers["X-Internal-Token"] = APP_API_TOKEN

    timeout = aiohttp.ClientTimeout(total=APP_API_TIMEOUT)
    url = f"{APP_API_BASE_URL.rstrip('/')}{path}"

    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        async with session.request(method, url, json=payload) as response:
            response.raise_for_status()
            return await response.json()


async def sync_user(
    user_id: int,
    platform: str,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
):
    if not _use_remote_api():
        return await local_sync_user(
            user_id=user_id,
            platform=platform,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

    return await _request(
        "POST",
        "/internal-api/users/sync/",
        {
            "user_id": user_id,
            "platform": platform,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
        },
    )


async def is_user_admin(user_id: int, platform: str) -> bool:
    if not _use_remote_api():
        return await local_is_user_admin(user_id, platform)

    data = await _request("GET", f"/internal-api/users/{platform}/{user_id}/is-admin/")
    return bool(data["is_admin"])


async def set_user_admin(user_id: int, platform: str = "tg"):
    if not _use_remote_api():
        return await local_set_user_admin(user_id, platform=platform)

    return await _request("POST", f"/internal-api/users/{platform}/{user_id}/set-admin/")


async def unset_user_admin(user_id: int, platform: str = "tg"):
    if not _use_remote_api():
        return await local_unset_user_admin(user_id, platform=platform)

    return await _request("POST", f"/internal-api/users/{platform}/{user_id}/unset-admin/")


async def get_all_tg_users() -> list[int]:
    if not _use_remote_api():
        return await local_get_all_tg_users()

    data = await _request("GET", "/internal-api/users/tg/ids/")
    return [int(item) for item in data["user_ids"]]


async def add_email(user_id: int, email: str, platform: str):
    if not _use_remote_api():
        return await local_add_email(user_id, email, platform)

    return await _request(
        "POST",
        f"/internal-api/users/{platform}/{user_id}/email/",
        {"email": email},
    )


async def get_email_step() -> int:
    if not _use_remote_api():
        return await local_get_email_step()

    data = await _request("GET", "/internal-api/settings/email-step/")
    return int(data["value"])


async def set_email_step(step: int):
    if not _use_remote_api():
        return await local_set_email_step(step)

    return await _request("PUT", "/internal-api/settings/email-step/", {"value": step})


async def get_email_text() -> str:
    if not _use_remote_api():
        return await local_get_email_text()

    data = await _request("GET", "/internal-api/settings/email-text/")
    return str(data["value"])


async def set_email_text(text: str):
    if not _use_remote_api():
        return await local_set_email_text(text)

    return await _request("PUT", "/internal-api/settings/email-text/", {"value": text})


async def get_user_emails() -> list[str]:
    if not _use_remote_api():
        return await local_get_user_emails()

    data = await _request("GET", "/internal-api/reports/emails/")
    return [str(item) for item in data["emails"]]


async def get_links() -> list[VideoLinkDTO]:
    if not _use_remote_api():
        return [_serialize_link(link) for link in await local_get_links()]

    data = await _request("GET", "/internal-api/links/")
    return [_link_from_dict(item) for item in data["links"]]


async def get_active_links() -> list[VideoLinkDTO]:
    if not _use_remote_api():
        return [_serialize_link(link) for link in await local_get_active_links()]

    data = await _request("GET", "/internal-api/links/active/")
    return [_link_from_dict(item) for item in data["links"]]


async def add_video_link(title: str, text: str, url: str) -> int:
    if not _use_remote_api():
        return await local_add_video_link(title=title, text=text, url=url)

    data = await _request(
        "POST",
        "/internal-api/links/",
        {"title": title, "message_text": text, "url": url},
    )
    return int(data["order"])


async def delete_video_link(link_id: int) -> bool:
    if not _use_remote_api():
        return await local_delete_video_link(link_id)

    data = await _request("DELETE", f"/internal-api/links/{link_id}/")
    return bool(data["deleted"])
