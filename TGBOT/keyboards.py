from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict
from config import ALLOWED_SERVICES


def phone_request_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text="📱 Отправить телефон", request_contact=True))
    kb.add(KeyboardButton(text="✍️ Ввести вручную"))
    return kb


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📋 Мои заявки", "✅ Согласование")
    kb.row("➕ Создать заявку", "⚙️ Настройки")
    return kb


def my_tasks_menu_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Открытые", "Завершённые")
    kb.add("⬅️ Назад")
    return kb


def settings_menu_keyboard(prefs: Dict[str, bool]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(f"Новый комментарий {'✔️' if prefs.get('notify_comment') else '❌'}", callback_data="toggle:notify_comment"))
    kb.add(InlineKeyboardButton(f"Изменён статус {'✔️' if prefs.get('notify_status') else '❌'}", callback_data="toggle:notify_status"))
    kb.add(InlineKeyboardButton(f"Изменён исполнитель {'✔️' if prefs.get('notify_executor') else '❌'}", callback_data="toggle:notify_executor"))
    kb.add(InlineKeyboardButton(f"Заявка выполнена {'✔️' if prefs.get('notify_done') else '❌'}", callback_data="toggle:notify_done"))
    kb.add(InlineKeyboardButton(f"Ждёт согласования {'✔️' if prefs.get('notify_approval') else '❌'}", callback_data="toggle:notify_approval"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="settings:back"))
    return kb


def services_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for _id, name in ALLOWED_SERVICES.items():
        kb.add(name)
    kb.add("⬅️ Назад")
    return kb


def task_actions_inline(task_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("👁 Детали", callback_data=f"task:details:{task_id}"))
    kb.add(InlineKeyboardButton("💬 Комментарий", callback_data=f"task:comment:{task_id}"))
    return kb


def approval_actions_inline(task_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("✅ Согласовать", callback_data=f"approval:ok:{task_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"approval:decline:{task_id}")
    )
    return kb


def link_to_task_inline(task_id: int, web_base: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔗 Открыть в Helpdesk", url=f"{web_base}/{task_id}"))
    return kb