"""
Keyboard layouts for the Telegram bot.
Fixed version for Windows users.
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from instruction_manager import get_instruction_manager

def auth_keyboard():
    """Keyboard for authentication"""
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🔐 Авторизация"))
    return kb.as_markup(resize_keyboard=True)


def main_menu_after_auth_keyboard():
    """Main menu keyboard after authentication"""
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🛠 Helpdesk"))
    kb.row(KeyboardButton(text="👤 Справочник сотрудников"))
    kb.row(KeyboardButton(text="📚 Инструкции"))  # ← Кнопка инструкций
    kb.row(KeyboardButton(text="🔧 Админ панель"))
    return kb.as_markup(resize_keyboard=True)


def my_tasks_menu_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="Открытые"), KeyboardButton(text="Завершённые"))
    kb.row(KeyboardButton(text="🏠 Главное меню"))
    return kb.as_markup(resize_keyboard=True)


def helpdesk_menu_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📋 Мои задачи"))
    kb.row(KeyboardButton(text="📝 Создать заявку"))
    kb.row(KeyboardButton(text="🏠 Главное меню"))
    return kb.as_markup(resize_keyboard=True)


def instructions_main_keyboard():
    """Main instructions menu keyboard"""
    kb = InlineKeyboardBuilder()
    
    # Get categories dynamically
    manager = get_instruction_manager()
    categories = manager.get_all_categories()
    
    if categories:
        for category in categories:
            kb.button(
                text=f"{category['icon']} {category['name']}",
                callback_data=f"category_{category['id']}"
            )
    else:
        kb.button(text="❌ Категории не найдены", callback_data="no_categories")
    
    kb.button(text="❌ Закрыть", callback_data="close_instructions")
    kb.adjust(1)
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


def otp_verification_keyboard():
    """OTP verification keyboard"""
    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Отправить код повторно", callback_data="resend_otp")
    kb.button(text="❌ Отмена", callback_data="cancel_otp")
    kb.adjust(1)
    return kb.as_markup()


# Admin keyboards
def admin_keyboard():
    """Admin panel keyboard"""
    kb = InlineKeyboardBuilder()
    kb.button(text="📁 Категории", callback_data="admin_categories")
    kb.button(text="📋 Инструкции", callback_data="admin_instructions")
    kb.button(text="❌ Закрыть", callback_data="close_admin")
    kb.adjust(1)
    return kb.as_markup()


def admin_categories_keyboard():
    """Admin categories management keyboard"""
    kb = InlineKeyboardBuilder()
    
    manager = get_instruction_manager()
    categories = manager.get_all_categories()
    
    if categories:
        for category in categories:
            kb.button(
                text=f"{category['icon']} {category['name']}",
                callback_data=f"admin_category_{category['id']}"
            )
    
    kb.button(text="➕ Добавить категорию", callback_data="admin_add_category")
    kb.button(text="⬅️ Назад", callback_data="admin_panel")
    kb.adjust(1)
    return kb.as_markup()


def admin_instructions_keyboard():
    """Admin instructions management keyboard"""
    kb = InlineKeyboardBuilder()
    
    manager = get_instruction_manager()
    categories = manager.get_all_categories()
    
    if categories:
        for category in categories:
            instructions = manager.get_instructions_by_category(category['id'])
            kb.button(
                text=f"{category['icon']} {category['name']} ({len(instructions)})",
                callback_data=f"admin_category_instructions_{category['id']}"
            )
    
    kb.button(text="⬅️ Назад", callback_data="admin_panel")
    kb.adjust(1)
    return kb.as_markup()


def admin_category_instructions_keyboard(category_id: str):
    """Admin category instructions keyboard"""
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
    
    kb.button(text="➕ Добавить инструкцию", callback_data=f"admin_add_instruction_{category_id}")
    kb.button(text="⬅️ Назад", callback_data="admin_instructions")
    kb.adjust(1)
    return kb.as_markup()


def admin_instruction_keyboard(category_id: str, instruction_id: str):
    """Admin individual instruction keyboard"""
    kb = InlineKeyboardBuilder()
    
    kb.button(text="✏️ Редактировать", callback_data=f"admin_edit_instruction_{category_id}_{instruction_id}")
    kb.button(text="🗑️ Удалить", callback_data=f"admin_delete_instruction_{category_id}_{instruction_id}")
    kb.button(text="📎 Загрузить файл", callback_data=f"admin_upload_file_{category_id}_{instruction_id}")
    kb.button(text="⬅️ Назад", callback_data=f"admin_category_instructions_{category_id}")
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
        kb.button(text="❌ Отмена", callback_data="admin_categories")
    
    kb.adjust(2)
    return kb.as_markup()