from vkbottle import BaseStateGroup


class AddLinkState(BaseStateGroup):
    WAITING_FOR_TITLE = "add_link_title"
    WAITING_FOR_TEXT = "add_link_text"
    WAITING_FOR_URL = "add_link_url"


class BroadcastState(BaseStateGroup):
    WAITING_FOR_MESSAGE = "broadcast_message"
