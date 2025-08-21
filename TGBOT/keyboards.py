from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from typing import Dict
from config import ALLOWED_SERVICES


def phone_request_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="📱 Отправить телефон", request_contact=True))
    kb.add(KeyboardButton(text="✍️ Ввести вручную"))
    return kb.as_markup(resize_keyboard=True)


def main_menu_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(
        KeyboardButton(text="📋 Мои заявки"),
        KeyboardButton(text="✅ Согласование"),
    )
    kb.row(
        KeyboardButton(text="➕ Создать заявку"),
        KeyboardButton(text="⚙️ Настройки"),
    )
    kb.row(KeyboardButton(text="🏠 Главное меню"))
    return kb.as_markup(resize_keyboard=True)


def main_menu_after_auth_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🛠 Helpdesk"))
    kb.row(KeyboardButton(text="👤 Справочник сотрудников"))
    return kb.as_markup(resize_keyboard=True)


def my_tasks_menu_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="Открытые"), KeyboardButton(text="Завершённые"))
    kb.row(KeyboardButton(text="⬅️ Назад"))
    return kb.as_markup(resize_keyboard=True)


def cancel_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="❌ Отменить"))
    return kb.as_markup(resize_keyboard=True)


def settings_menu_keyboard(prefs: Dict[str, bool]):
    kb = InlineKeyboardBuilder()
    kb.button(text=f"Новый комментарий {'✔️' if prefs.get('notify_comment') else '❌'}", callback_data="toggle:notify_comment")
    kb.button(text=f"Изменён статус {'✔️' if prefs.get('notify_status') else '❌'}", callback_data="toggle:notify_status")
    kb.button(text=f"Изменён исполнитель {'✔️' if prefs.get('notify_executor') else '❌'}", callback_data="toggle:notify_executor")
    kb.button(text=f"Заявка выполнена {'✔️' if prefs.get('notify_done') else '❌'}", callback_data="toggle:notify_done")
    kb.button(text=f"Новая заявка {'✔️' if prefs.get('notify_new_task') else '❌'}", callback_data="toggle:notify_new_task")
    kb.button(text=f"Ждёт согласования {'✔️' if prefs.get('notify_approval') else '❌'}", callback_data="toggle:notify_approval")
    kb.button(text="⬅️ Назад", callback_data="settings:back")
    kb.adjust(1)
    return kb.as_markup()


def services_keyboard():
    # Показываем только необходимые пункты: Удаленный доступ, Прочее, и Назад
    kb = ReplyKeyboardBuilder()
    # Найдем id по названию, чтобы сохранить соответствие ServiceId
    label_map = {name: _id for _id, name in ALLOWED_SERVICES.items()}
    for title in ("Удаленный доступ", "Прочее"):
        if title in label_map:
            kb.row(KeyboardButton(text=title))
    kb.row(KeyboardButton(text="⬅️ Назад"))
    return kb.as_markup(resize_keyboard=True)


def task_actions_inline(task_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="👁 Детали", callback_data=f"task:details:{task_id}")
    kb.button(text="💬 Комментарий", callback_data=f"task:comment:{task_id}")
    kb.adjust(1)
    return kb.as_markup()


def approval_actions_inline(task_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Согласовать", callback_data=f"approval:ok:{task_id}")
    kb.button(text="❌ Отклонить", callback_data=f"approval:decline:{task_id}")
    kb.adjust(2)
    return kb.as_markup()


def link_to_task_inline(task_id: int, web_base: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="🔗 Открыть в Helpdesk", url=f"{web_base}/{task_id}")
    return kb.as_markup()


def reply_to_task_inline(task_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="💬 Ответить", callback_data=f"task:comment:{task_id}")
    kb.adjust(1)
    return kb.as_markup()