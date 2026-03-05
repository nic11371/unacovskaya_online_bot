from vkbottle import BaseStateGroup


class AddLinkState(BaseStateGroup):
    WAITING_FOR_TITLE = 0
    WAITING_FOR_TEXT = 1
    WAITING_FOR_URL = 2


class BroadcastState(BaseStateGroup):
    WAITING_FOR_MESSAGE = 0
