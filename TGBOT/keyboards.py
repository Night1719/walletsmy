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
    kb.row(KeyboardButton(text="📚 Инструкции"))
    kb.row(KeyboardButton(text="🔧 Админ панель"))
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


def duration_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="1 день"), KeyboardButton(text="3 дня"))
    kb.row(KeyboardButton(text="7 дней"), KeyboardButton(text="14 дней"))
    kb.row(KeyboardButton(text="❌ Отменить"))
    return kb.as_markup(resize_keyboard=True)


def task_actions_inline(task_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="👁 Детали", callback_data=f"task:details:{task_id}")
    kb.button(text="💬 Комментарий", callback_data=f"task:comment:{task_id}")
    kb.adjust(1)
    return kb.as_markup()


def approval_actions_inline(task_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="🔗 Перейти", callback_data=f"approval:goto:{task_id}")
    kb.adjust(1)
    return kb.as_markup()


def approval_detail_keyboard(task_id: int):
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


def instructions_main_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="1️⃣ 1С"))
    kb.row(KeyboardButton(text="📧 Почта"))
    kb.row(KeyboardButton(text="⬅️ Назад"))
    return kb.as_markup(resize_keyboard=True)


def instructions_1c_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="AR2"))
    kb.row(KeyboardButton(text="DM"))
    kb.row(KeyboardButton(text="⬅️ Назад"))
    return kb.as_markup(resize_keyboard=True)


def instructions_email_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📱 iPhone"))
    kb.row(KeyboardButton(text="🤖 Android"))
    kb.row(KeyboardButton(text="💻 Outlook"))
    kb.row(KeyboardButton(text="⬅️ Назад"))
    return kb.as_markup(resize_keyboard=True)


def instructions_otp_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📱 Отправить телефон", request_contact=True))
    kb.row(KeyboardButton(text="✍️ Ввести вручную"))
    kb.row(KeyboardButton(text="⬅️ Назад"))
    return kb.as_markup(resize_keyboard=True)


def otp_verification_keyboard():
    """OTP verification keyboard"""
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🔄 Отправить код повторно"))
    kb.row(KeyboardButton(text="❌ Отмена"))
    return kb.as_markup(resize_keyboard=True)


# === Admin Keyboards ===

def admin_keyboard():
    """Admin panel main keyboard"""
    kb = InlineKeyboardBuilder()
    kb.button(text="📁 Управление категориями", callback_data="admin_categories")
    kb.button(text="📝 Управление инструкциями", callback_data="admin_instructions")
    kb.button(text="📊 Статистика", callback_data="admin_stats")
    kb.button(text="⚙️ Настройки", callback_data="admin_settings")
    kb.button(text="⬅️ Назад", callback_data="admin_back")
    kb.adjust(1)
    return kb.as_markup()


def admin_categories_keyboard():
    """Categories management keyboard"""
    kb = InlineKeyboardBuilder()
    
    # Add existing categories
    try:
        from instruction_manager import get_instruction_manager
        manager = get_instruction_manager()
        categories = manager.get_categories()
        
        for cat_id, category in categories.items():
            kb.button(
                text=f"{category['icon']} {category['name']}",
                callback_data=f"admin_category_{cat_id}"
            )
    except:
        pass
    
    kb.button(text="➕ Добавить категорию", callback_data="admin_add_category")
    kb.button(text="⬅️ Назад", callback_data="admin_back")
    kb.adjust(1)
    return kb.as_markup()


def admin_instructions_keyboard(category_id: str):
    """Instructions management keyboard for specific category"""
    kb = InlineKeyboardBuilder()
    
    # Add existing instructions
    try:
        from instruction_manager import get_instruction_manager
        manager = get_instruction_manager()
        instructions = manager.get_instructions(category_id)
        
        for inst_id, instruction in instructions.items():
            files_count = len(instruction["files"])
            kb.button(
                text=f"📝 {instruction['name']} ({files_count} файлов)",
                callback_data=f"admin_instruction_{category_id}_{inst_id}"
            )
    except:
        pass
    
    kb.button(text="➕ Добавить инструкцию", callback_data=f"admin_add_instruction_{category_id}")
    kb.button(text="📤 Загрузить файл", callback_data=f"admin_upload_file_{category_id}")
    kb.button(text="⬅️ Назад", callback_data="admin_categories")
    kb.adjust(1)
    return kb.as_markup()


def admin_instruction_keyboard(category_id: str, instruction_id: str):
    """Single instruction management keyboard"""
    kb = InlineKeyboardBuilder()
    
    kb.button(text="📤 Загрузить файл", callback_data=f"admin_upload_file_{category_id}_{instruction_id}")
    kb.button(text="✏️ Редактировать", callback_data=f"admin_edit_instruction_{category_id}_{instruction_id}")
    kb.button(text="🗑️ Удалить", callback_data=f"admin_delete_instruction_{category_id}_{instruction_id}")
    kb.button(text="⬅️ Назад", callback_data=f"admin_category_{category_id}")
    kb.adjust(1)
    return kb.as_markup()


def admin_file_format_keyboard(category_id: str = None, instruction_id: str = None):
    """File format selection keyboard"""
    kb = InlineKeyboardBuilder()
    
    if category_id and instruction_id:
        # For existing instruction format selection
        kb.button(text="📄 PDF", callback_data=f"format_pdf_{category_id}_{instruction_id}")
        kb.button(text="📝 DOCX", callback_data=f"format_docx_{category_id}_{instruction_id}")
        kb.button(text="📄 DOC", callback_data=f"format_doc_{category_id}_{instruction_id}")
        kb.button(text="⬅️ Назад", callback_data=f"admin_instruction_{category_id}_{instruction_id}")
    else:
        # For new instruction format selection
        kb.button(text="📄 PDF", callback_data="admin_file_format_pdf")
        kb.button(text="📝 DOCX", callback_data="admin_file_format_docx")
        kb.button(text="📄 DOC", callback_data="admin_file_format_doc")
        kb.button(text="📄 TXT", callback_data="admin_file_format_txt")
        kb.button(text="🎥 MP4", callback_data="admin_file_format_mp4")
        kb.button(text="🎥 AVI", callback_data="admin_file_format_avi")
        kb.button(text="🎥 MOV", callback_data="admin_file_format_mov")
        kb.button(text="❌ Отмена", callback_data="admin_categories")
    
    kb.adjust(2)
    return kb.as_markup()


def instructions_category_keyboard(category_id: str):
    """Instructions category keyboard"""
    kb = InlineKeyboardBuilder()
    
    manager = get_instruction_manager()
    instructions = manager.get_instructions_by_category(category_id)
    category = manager.get_category(category_id)
    
    if instructions:
        for instruction in instructions:
            kb.button(
                text=f"📄 {instruction['name']}",
                callback_data=f"instruction_{category_id}_{instruction['id']}"
            )
    else:
        kb.button(text="❌ Инструкции не найдены", callback_data="no_instructions")
    
    kb.button(text="⬅️ Назад", callback_data="back_to_categories")
    kb.adjust(1)
    return kb.as_markup()


def instruction_keyboard(category_id: str, instruction_id: str):
    """Individual instruction keyboard"""
    kb = InlineKeyboardBuilder()
    
    manager = get_instruction_manager()
    instruction = manager.get_instruction(category_id, instruction_id)
    
    if instruction:
        # Show available formats
        for format_type in instruction.get('formats', []):
            kb.button(
                text=f"📄 {format_type.upper()}",
                callback_data=f"create_secure_link_{category_id}_{instruction_id}_{format_type}"
            )
    
    kb.button(text="⬅️ Назад", callback_data=f"category_{category_id}")
    kb.adjust(1)
    return kb.as_markup()