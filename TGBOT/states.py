from aiogram.dispatcher.filters.state import State, StatesGroup


class AuthStates(StatesGroup):
    awaiting_phone = State()


class CreateTaskStates(StatesGroup):
    choosing_service = State()
    entering_name = State()
    entering_description = State()
    confirming = State()


class CommentStates(StatesGroup):
    entering_comment = State()


class DeclineStates(StatesGroup):
    entering_reason = State()