from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    awaiting_phone = State()


class CreateTaskStates(StatesGroup):
    choosing_service = State()
    entering_name = State()
    entering_description = State()
    confirming = State()
    entering_remote_start = State()
    entering_remote_end = State()
    choosing_remote_duration = State()


class CommentStates(StatesGroup):
    entering_comment = State()


class DeclineStates(StatesGroup):
    entering_reason = State()


class DirectoryStates(StatesGroup):
    searching = State()


class RegistrationStates(StatesGroup):
    awaiting_phone = State()
    awaiting_email = State()
    confirming = State()