from aiogram.fsm.state import State, StatesGroup


class AddLinkState(StatesGroup):
    waiting_for_title = State()
    waiting_for_text = State()
    waiting_for_url = State()


class BroadcastState(StatesGroup):
    waiting_for_message = State()


class EmailStepState(StatesGroup):
    waiting_for_step = State()


class EmailTextState(StatesGroup):
    waiting_for_text = State()
