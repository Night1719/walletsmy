from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from typing import Dict
from instruction_manager import get_instruction_manager


def phone_request_keyboard():
    """Phone request keyboard"""
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📱 Отправить телефон", request_contact=True))
    kb.row(KeyboardButton(text="✍️ Ввести вручную"))
    return kb.as_markup(resize_keyboard=True)


def main_menu_keyboard():
    """Main menu keyboard for non-authenticated users"""
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🚀 Начать работу"))
    kb.row(KeyboardButton(text="ℹ️ О боте"))
    return kb.as_markup(resize_keyboard=True)


def main_menu_after_auth_keyboard():
    """Main menu keyboard for authenticated users"""
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📋 Мои задачи"))
    kb.row(KeyboardButton(text="👥 Справочник сотрудников"))
    kb.row(KeyboardButton(text="🎫 Helpdesk"))
    kb.row(KeyboardButton(text="📚 Инструкции"))
    kb.row(KeyboardButton(text="🔧 Админ панель"))
    kb.row(KeyboardButton(text="⚙️ Настройки"))
    return kb.as_markup(resize_keyboard=True)


def my_tasks_menu_keyboard():
    """My tasks menu keyboard"""
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📋 Мои задачи"))
    kb.row(KeyboardButton(text="🏠 Главное меню"))
    return kb.as_markup(resize_keyboard=True)


def cancel_keyboard():
    """Cancel keyboard"""
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="❌ Отмена"))
    return kb.as_markup(resize_keyboard=True)


def settings_menu_keyboard(prefs: Dict[str, bool]):
    """Settings menu keyboard"""
    kb = ReplyKeyboardBuilder()
    
    # Notification preferences
    notification_text = "🔔 Уведомления: " + ("Вкл" if prefs.get("notifications", True) else "Выкл")
    kb.row(KeyboardButton(text=notification_text))
    
    # Language preference
    language_text = "🌐 Язык: " + ("Русский" if prefs.get("language", "ru") == "ru" else "English")
    kb.row(KeyboardButton(text=language_text))
    
    # Back button
    kb.row(KeyboardButton(text="⬅️ Назад"))
    
    return kb.as_markup(resize_keyboard=True)


def services_keyboard():
    """Services keyboard"""
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="💻 IT-поддержка"))
    kb.row(KeyboardButton(text="🏢 HR-служба"))
    kb.row(KeyboardButton(text="💰 Бухгалтерия"))
    kb.row(KeyboardButton(text="📋 Администрация"))
    kb.row(KeyboardButton(text="⬅️ Назад"))
    return kb.as_markup(resize_keyboard=True)


def duration_keyboard():
    """Duration selection keyboard"""
    kb = ReplyKeyboardBuilder()
    durations = [
        "⏰ 30 минут",
        "⏰ 1 час",
        "⏰ 2 часа",
        "⏰ 4 часа",
        "⏰ 8 часов",
        "⏰ 1 день",
        "⏰ 2 дня",
        "⏰ 1 неделя"
    ]
    
    for duration in durations:
        kb.row(KeyboardButton(text=duration))
    
    kb.row(KeyboardButton(text="❌ Отмена"))
    return kb.as_markup(resize_keyboard=True)


def approval_detail_keyboard(task_id: int):
    """Approval detail keyboard"""
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Одобрить", callback_data=f"approve_task_{task_id}")
    kb.button(text="❌ Отклонить", callback_data=f"reject_task_{task_id}")
    kb.button(text="📝 Комментарий", callback_data=f"comment_task_{task_id}")
    kb.button(text="⬅️ Назад", callback_data="back_to_tasks")
    kb.adjust(2)
    return kb.as_markup()


# === Instructions Keyboards ===

def instructions_main_keyboard():
    """Instructions main keyboard"""
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📚 1С"))
    kb.row(KeyboardButton(text="📧 Почта"))
    kb.row(KeyboardButton(text="⬅️ Назад"))
    return kb.as_markup(resize_keyboard=True)


def instructions_1c_keyboard():
    """1C instructions keyboard"""
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📊 AR2"))
    kb.row(KeyboardButton(text="📈 DM"))
    kb.row(KeyboardButton(text="⬅️ Назад"))
    return kb.as_markup(resize_keyboard=True)


def instructions_email_keyboard():
    """Email instructions keyboard"""
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


# === Admin Keyboards ===

def admin_keyboard():
    """Admin panel main keyboard"""
    kb = InlineKeyboardBuilder()
    kb.button(text="📁 Управление категориями", callback_data="admin_categories")
    kb.button(text="📝 Управление инструкциями", callback_data="admin_instructions")
    kb.button(text="📊 Статистика", callback_data="admin_stats")
    kb.button(text="⬅️ Назад", callback_data="back_to_main")
    kb.adjust(1)
    return kb.as_markup()


def admin_categories_keyboard():
    """Admin categories keyboard"""
    kb = InlineKeyboardBuilder()
    
    manager = get_instruction_manager()
    categories = manager.get_categories()
    
    if categories:
        for category in categories:
            kb.button(
                text=f"📁 {category['name']}",
                callback_data=f"admin_category_{category['id']}"
            )
    else:
        kb.button(text="❌ Категории не найдены", callback_data="no_categories")
    
    kb.button(text="➕ Добавить категорию", callback_data="admin_add_category")
    kb.button(text="⬅️ Назад", callback_data="back_to_admin")
    kb.adjust(1)
    return kb.as_markup()


def admin_instructions_keyboard(category_id: str):
    """Admin instructions keyboard for a category"""
    kb = InlineKeyboardBuilder()
    
    manager = get_instruction_manager()
    instructions = manager.get_instructions_by_category(category_id)
    category = manager.get_category(category_id)
    
    if instructions:
        for instruction in instructions:
            kb.button(
                text=f"📄 {instruction['name']}",
                callback_data=f"admin_instruction_{category_id}_{instruction['id']}"
            )
    else:
        kb.button(text="❌ Инструкции не найдены", callback_data="no_instructions")
    
    kb.button(text="➕ Добавить инструкцию", callback_data=f"admin_add_instruction_{category_id}")
    kb.button(text="⬅️ Назад", callback_data="admin_categories")
    kb.adjust(1)
    return kb.as_markup()


def admin_instruction_keyboard(category_id: str, instruction_id: str):
    """Admin individual instruction keyboard"""
    kb = InlineKeyboardBuilder()
    kb.button(text="✏️ Редактировать", callback_data=f"admin_edit_instruction_{category_id}_{instruction_id}")
    kb.button(text="🗑️ Удалить", callback_data=f"admin_delete_instruction_{category_id}_{instruction_id}")
    kb.button(text="📁 Загрузить файл", callback_data=f"admin_upload_file_{category_id}_{instruction_id}")
    kb.button(text="⬅️ Назад", callback_data=f"admin_instructions_{category_id}")
    kb.adjust(2)
    return kb.as_markup()


def admin_file_format_keyboard(category_id: str = None, instruction_id: str = None):
    """Admin file format selection keyboard"""
    kb = InlineKeyboardBuilder()
    
    # Document formats
    kb.button(text="📄 PDF", callback_data="admin_file_format_pdf")
    kb.button(text="📄 DOCX", callback_data="admin_file_format_docx")
    kb.button(text="📄 DOC", callback_data="admin_file_format_doc")
    kb.button(text="📄 TXT", callback_data="admin_file_format_txt")
    
    # Video formats
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