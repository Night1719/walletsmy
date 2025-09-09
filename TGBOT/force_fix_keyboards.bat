@echo off
echo ========================================
echo    Принудительное исправление keyboards.py
echo ========================================
echo.

echo 🔧 Создание резервной копии...
if exist "keyboards.py" (
    copy "keyboards.py" "keyboards_backup_force.py" >nul
    echo ✅ Резервная копия создана
) else (
    echo ❌ Файл keyboards.py не найден
    pause
    exit /b 1
)

echo.
echo 🔄 Создание нового keyboards.py...

REM Создаем новый keyboards.py с нуля
echo from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton > keyboards_new.py
echo from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder >> keyboards_new.py
echo from typing import Dict >> keyboards_new.py
echo from instruction_manager import get_instruction_manager >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def phone_request_keyboard(): >> keyboards_new.py
echo     """Phone request keyboard""" >> keyboards_new.py
echo     kb = ReplyKeyboardBuilder() >> keyboards_new.py
echo     kb.row(KeyboardButton(text="📱 Отправить телефон", request_contact=True)) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="✍️ Ввести вручную")) >> keyboards_new.py
echo     return kb.as_markup(resize_keyboard=True) >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def main_menu_keyboard(): >> keyboards_new.py
echo     """Main menu keyboard for non-authenticated users""" >> keyboards_new.py
echo     kb = ReplyKeyboardBuilder() >> keyboards_new.py
echo     kb.row(KeyboardButton(text="🚀 Начать работу")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="ℹ️ О боте")) >> keyboards_new.py
echo     return kb.as_markup(resize_keyboard=True) >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def main_menu_after_auth_keyboard(): >> keyboards_new.py
echo     """Main menu keyboard for authenticated users""" >> keyboards_new.py
echo     kb = ReplyKeyboardBuilder() >> keyboards_new.py
echo     kb.row(KeyboardButton(text="📋 Мои задачи")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="👥 Справочник сотрудников")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="🎫 Helpdesk")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="📚 Инструкции")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="🔧 Админ панель")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="⚙️ Настройки")) >> keyboards_new.py
echo     return kb.as_markup(resize_keyboard=True) >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def my_tasks_menu_keyboard(): >> keyboards_new.py
echo     """My tasks menu keyboard""" >> keyboards_new.py
echo     kb = ReplyKeyboardBuilder() >> keyboards_new.py
echo     kb.row(KeyboardButton(text="📋 Мои задачи")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="🏠 Главное меню")) >> keyboards_new.py
echo     return kb.as_markup(resize_keyboard=True) >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def cancel_keyboard(): >> keyboards_new.py
echo     """Cancel keyboard""" >> keyboards_new.py
echo     kb = ReplyKeyboardBuilder() >> keyboards_new.py
echo     kb.row(KeyboardButton(text="❌ Отмена")) >> keyboards_new.py
echo     return kb.as_markup(resize_keyboard=True) >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def settings_menu_keyboard(prefs: Dict[str, bool]): >> keyboards_new.py
echo     """Settings menu keyboard""" >> keyboards_new.py
echo     kb = ReplyKeyboardBuilder() >> keyboards_new.py
echo     notification_text = "🔔 Уведомления: " + ("Вкл" if prefs.get("notifications", True) else "Выкл") >> keyboards_new.py
echo     kb.row(KeyboardButton(text=notification_text)) >> keyboards_new.py
echo     language_text = "🌐 Язык: " + ("Русский" if prefs.get("language", "ru") == "ru" else "English") >> keyboards_new.py
echo     kb.row(KeyboardButton(text=language_text)) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="⬅️ Назад")) >> keyboards_new.py
echo     return kb.as_markup(resize_keyboard=True) >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def services_keyboard(): >> keyboards_new.py
echo     """Services keyboard""" >> keyboards_new.py
echo     kb = ReplyKeyboardBuilder() >> keyboards_new.py
echo     kb.row(KeyboardButton(text="💻 IT-поддержка")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="🏢 HR-служба")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="💰 Бухгалтерия")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="📋 Администрация")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="⬅️ Назад")) >> keyboards_new.py
echo     return kb.as_markup(resize_keyboard=True) >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def duration_keyboard(): >> keyboards_new.py
echo     """Duration selection keyboard""" >> keyboards_new.py
echo     kb = ReplyKeyboardBuilder() >> keyboards_new.py
echo     durations = ["⏰ 30 минут", "⏰ 1 час", "⏰ 2 часа", "⏰ 4 часа", "⏰ 8 часов", "⏰ 1 день", "⏰ 2 дня", "⏰ 1 неделя"] >> keyboards_new.py
echo     for duration in durations: >> keyboards_new.py
echo         kb.row(KeyboardButton(text=duration)) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="❌ Отмена")) >> keyboards_new.py
echo     return kb.as_markup(resize_keyboard=True) >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def approval_detail_keyboard(task_id: int): >> keyboards_new.py
echo     """Approval detail keyboard""" >> keyboards_new.py
echo     kb = InlineKeyboardBuilder() >> keyboards_new.py
echo     kb.button(text="✅ Одобрить", callback_data=f"approve_task_{task_id}") >> keyboards_new.py
echo     kb.button(text="❌ Отклонить", callback_data=f"reject_task_{task_id}") >> keyboards_new.py
echo     kb.button(text="📝 Комментарий", callback_data=f"comment_task_{task_id}") >> keyboards_new.py
echo     kb.button(text="⬅️ Назад", callback_data="back_to_tasks") >> keyboards_new.py
echo     kb.adjust(2) >> keyboards_new.py
echo     return kb.as_markup() >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def instructions_main_keyboard(): >> keyboards_new.py
echo     """Instructions main keyboard""" >> keyboards_new.py
echo     kb = ReplyKeyboardBuilder() >> keyboards_new.py
echo     kb.row(KeyboardButton(text="📚 1С")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="📧 Почта")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="⬅️ Назад")) >> keyboards_new.py
echo     return kb.as_markup(resize_keyboard=True) >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def instructions_1c_keyboard(): >> keyboards_new.py
echo     """1C instructions keyboard""" >> keyboards_new.py
echo     kb = ReplyKeyboardBuilder() >> keyboards_new.py
echo     kb.row(KeyboardButton(text="📊 AR2")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="📈 DM")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="⬅️ Назад")) >> keyboards_new.py
echo     return kb.as_markup(resize_keyboard=True) >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def instructions_email_keyboard(): >> keyboards_new.py
echo     """Email instructions keyboard""" >> keyboards_new.py
echo     kb = ReplyKeyboardBuilder() >> keyboards_new.py
echo     kb.row(KeyboardButton(text="📱 iPhone")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="🤖 Android")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="💻 Outlook")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="⬅️ Назад")) >> keyboards_new.py
echo     return kb.as_markup(resize_keyboard=True) >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def instructions_otp_keyboard(): >> keyboards_new.py
echo     """Instructions OTP keyboard""" >> keyboards_new.py
echo     kb = ReplyKeyboardBuilder() >> keyboards_new.py
echo     kb.row(KeyboardButton(text="📱 Отправить телефон", request_contact=True)) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="✍️ Ввести вручную")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="⬅️ Назад")) >> keyboards_new.py
echo     return kb.as_markup(resize_keyboard=True) >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def otp_verification_keyboard(): >> keyboards_new.py
echo     """OTP verification keyboard""" >> keyboards_new.py
echo     kb = ReplyKeyboardBuilder() >> keyboards_new.py
echo     kb.row(KeyboardButton(text="🔄 Отправить код повторно")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="❌ Отмена")) >> keyboards_new.py
echo     return kb.as_markup(resize_keyboard=True) >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def admin_keyboard(): >> keyboards_new.py
echo     """Admin panel main keyboard""" >> keyboards_new.py
echo     kb = InlineKeyboardBuilder() >> keyboards_new.py
echo     kb.button(text="📁 Управление категориями", callback_data="admin_categories") >> keyboards_new.py
echo     kb.button(text="📝 Управление инструкциями", callback_data="admin_instructions") >> keyboards_new.py
echo     kb.button(text="📊 Статистика", callback_data="admin_stats") >> keyboards_new.py
echo     kb.button(text="⬅️ Назад", callback_data="back_to_main") >> keyboards_new.py
echo     kb.adjust(1) >> keyboards_new.py
echo     return kb.as_markup() >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def admin_categories_keyboard(): >> keyboards_new.py
echo     """Admin categories keyboard""" >> keyboards_new.py
echo     kb = InlineKeyboardBuilder() >> keyboards_new.py
echo     manager = get_instruction_manager() >> keyboards_new.py
echo     categories = manager.get_categories() >> keyboards_new.py
echo     if categories: >> keyboards_new.py
echo         for category in categories: >> keyboards_new.py
echo             kb.button(text=f"📁 {category['name']}", callback_data=f"admin_category_{category['id']}") >> keyboards_new.py
echo     else: >> keyboards_new.py
echo         kb.button(text="❌ Категории не найдены", callback_data="no_categories") >> keyboards_new.py
echo     kb.button(text="➕ Добавить категорию", callback_data="admin_add_category") >> keyboards_new.py
echo     kb.button(text="⬅️ Назад", callback_data="back_to_admin") >> keyboards_new.py
echo     kb.adjust(1) >> keyboards_new.py
echo     return kb.as_markup() >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def admin_instructions_keyboard(category_id: str): >> keyboards_new.py
echo     """Admin instructions keyboard for a category""" >> keyboards_new.py
echo     kb = InlineKeyboardBuilder() >> keyboards_new.py
echo     manager = get_instruction_manager() >> keyboards_new.py
echo     instructions = manager.get_instructions_by_category(category_id) >> keyboards_new.py
echo     if instructions: >> keyboards_new.py
echo         for instruction in instructions: >> keyboards_new.py
echo             kb.button(text=f"📄 {instruction['name']}", callback_data=f"admin_instruction_{category_id}_{instruction['id']}") >> keyboards_new.py
echo     else: >> keyboards_new.py
echo         kb.button(text="❌ Инструкции не найдены", callback_data="no_instructions") >> keyboards_new.py
echo     kb.button(text="➕ Добавить инструкцию", callback_data=f"admin_add_instruction_{category_id}") >> keyboards_new.py
echo     kb.button(text="⬅️ Назад", callback_data="admin_categories") >> keyboards_new.py
echo     kb.adjust(1) >> keyboards_new.py
echo     return kb.as_markup() >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def admin_instruction_keyboard(category_id: str, instruction_id: str): >> keyboards_new.py
echo     """Admin individual instruction keyboard""" >> keyboards_new.py
echo     kb = InlineKeyboardBuilder() >> keyboards_new.py
echo     kb.button(text="✏️ Редактировать", callback_data=f"admin_edit_instruction_{category_id}_{instruction_id}") >> keyboards_new.py
echo     kb.button(text="🗑️ Удалить", callback_data=f"admin_delete_instruction_{category_id}_{instruction_id}") >> keyboards_new.py
echo     kb.button(text="📁 Загрузить файл", callback_data=f"admin_upload_file_{category_id}_{instruction_id}") >> keyboards_new.py
echo     kb.button(text="⬅️ Назад", callback_data=f"admin_instructions_{category_id}") >> keyboards_new.py
echo     kb.adjust(2) >> keyboards_new.py
echo     return kb.as_markup() >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def admin_file_format_keyboard(category_id: str = None, instruction_id: str = None): >> keyboards_new.py
echo     """Admin file format selection keyboard""" >> keyboards_new.py
echo     kb = InlineKeyboardBuilder() >> keyboards_new.py
echo     kb.button(text="📄 PDF", callback_data="admin_file_format_pdf") >> keyboards_new.py
echo     kb.button(text="📄 DOCX", callback_data="admin_file_format_docx") >> keyboards_new.py
echo     kb.button(text="📄 DOC", callback_data="admin_file_format_doc") >> keyboards_new.py
echo     kb.button(text="📄 TXT", callback_data="admin_file_format_txt") >> keyboards_new.py
echo     kb.button(text="🎥 MP4", callback_data="admin_file_format_mp4") >> keyboards_new.py
echo     kb.button(text="🎥 AVI", callback_data="admin_file_format_avi") >> keyboards_new.py
echo     kb.button(text="🎥 MOV", callback_data="admin_file_format_mov") >> keyboards_new.py
echo     kb.button(text="❌ Отмена", callback_data="admin_categories") >> keyboards_new.py
echo     kb.adjust(2) >> keyboards_new.py
echo     return kb.as_markup() >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def instructions_category_keyboard(category_id: str): >> keyboards_new.py
echo     """Instructions category keyboard""" >> keyboards_new.py
echo     kb = InlineKeyboardBuilder() >> keyboards_new.py
echo     manager = get_instruction_manager() >> keyboards_new.py
echo     instructions = manager.get_instructions_by_category(category_id) >> keyboards_new.py
echo     if instructions: >> keyboards_new.py
echo         for instruction in instructions: >> keyboards_new.py
echo             kb.button(text=f"📄 {instruction['name']}", callback_data=f"instruction_{category_id}_{instruction['id']}") >> keyboards_new.py
echo     else: >> keyboards_new.py
echo         kb.button(text="❌ Инструкции не найдены", callback_data="no_instructions") >> keyboards_new.py
echo     kb.button(text="⬅️ Назад", callback_data="back_to_categories") >> keyboards_new.py
echo     kb.adjust(1) >> keyboards_new.py
echo     return kb.as_markup() >> keyboards_new.py
echo. >> keyboards_new.py
echo. >> keyboards_new.py
echo def instruction_keyboard(category_id: str, instruction_id: str): >> keyboards_new.py
echo     """Individual instruction keyboard""" >> keyboards_new.py
echo     kb = InlineKeyboardBuilder() >> keyboards_new.py
echo     manager = get_instruction_manager() >> keyboards_new.py
echo     instruction = manager.get_instruction(category_id, instruction_id) >> keyboards_new.py
echo     if instruction: >> keyboards_new.py
echo         for format_type in instruction.get('formats', []): >> keyboards_new.py
echo             kb.button(text=f"📄 {format_type.upper()}", callback_data=f"create_secure_link_{category_id}_{instruction_id}_{format_type}") >> keyboards_new.py
echo     kb.button(text="⬅️ Назад", callback_data=f"category_{category_id}") >> keyboards_new.py
echo     kb.adjust(1) >> keyboards_new.py
echo     return kb.as_markup() >> keyboards_new.py

echo ✅ Новый keyboards.py создан
echo.

echo 🔄 Замена старого файла...
move keyboards_new.py keyboards.py >nul
echo ✅ keyboards.py заменен

echo.
echo 🧪 Проверка синтаксиса...
python -c "import keyboards; print('✅ keyboards.py синтаксически корректен')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка синтаксиса
    echo 🔄 Восстановление из резервной копии...
    copy "keyboards_backup_force.py" "keyboards.py" >nul
    pause
    exit /b 1
)

echo ✅ Синтаксис корректен
echo.

echo 🧪 Проверка импорта функций...
python -c "from keyboards import instructions_main_keyboard, instructions_category_keyboard, instruction_keyboard, otp_verification_keyboard, main_menu_after_auth_keyboard; print('✅ Все функции импортированы')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта функций
    echo 🔄 Восстановление из резервной копии...
    copy "keyboards_backup_force.py" "keyboards.py" >nul
    pause
    exit /b 1
)

echo ✅ Все функции импортированы успешно
echo.

echo 🧪 Проверка импорта бота...
python -c "import bot; print('✅ bot.py импортирован')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта bot.py
    echo 🔄 Восстановление из резервной копии...
    copy "keyboards_backup_force.py" "keyboards.py" >nul
    pause
    exit /b 1
)

echo ✅ bot.py импортирован успешно
echo.

echo ========================================
echo           🎉 Исправление завершено!
echo ========================================
echo.
echo ✅ keyboards.py полностью пересоздан
echo ✅ Все функции работают
echo ✅ bot.py запускается
echo 📁 Резервная копия: keyboards_backup_force.py
echo.
echo 🚀 Теперь можно запускать:
echo    python bot.py
echo.
pause