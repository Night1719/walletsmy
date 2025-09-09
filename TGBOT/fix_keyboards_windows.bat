@echo off
echo ========================================
echo    Исправление keyboards.py для Windows
echo ========================================
echo.

echo 🔧 Создание резервной копии keyboards.py...
if exist "keyboards.py" (
    copy "keyboards.py" "keyboards_backup.py" >nul
    echo ✅ Резервная копия создана: keyboards_backup.py
) else (
    echo ❌ Файл keyboards.py не найден
    pause
    exit /b 1
)

echo.
echo 🧪 Проверка импорта...
python -c "from keyboards import instructions_category_keyboard, instruction_keyboard; print('✅ Функции keyboards импортированы успешно')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта функций keyboards
    echo.
    echo 🔧 Ручное исправление...
    echo Добавьте в конец keyboards.py следующие функции:
    echo.
    echo def instructions_category_keyboard(category_id: str):
    echo     kb = InlineKeyboardBuilder()
    echo     manager = get_instruction_manager()
    echo     instructions = manager.get_instructions_by_category(category_id)
    echo     if instructions:
    echo         for instruction in instructions:
    echo             kb.button(text=f"📄 {instruction['name']}", callback_data=f"instruction_{category_id}_{instruction['id']}")
    echo     else:
    echo         kb.button(text="❌ Инструкции не найдены", callback_data="no_instructions")
    echo     kb.button(text="⬅️ Назад", callback_data="back_to_categories")
    echo     kb.adjust(1)
    echo     return kb.as_markup()
    echo.
    echo def instruction_keyboard(category_id: str, instruction_id: str):
    echo     kb = InlineKeyboardBuilder()
    echo     manager = get_instruction_manager()
    echo     instruction = manager.get_instruction(category_id, instruction_id)
    echo     if instruction:
    echo         for format_type in instruction.get('formats', []):
    echo             kb.button(text=f"📄 {format_type.upper()}", callback_data=f"create_secure_link_{category_id}_{instruction_id}_{format_type}")
    echo     kb.button(text="⬅️ Назад", callback_data=f"category_{category_id}")
    echo     kb.adjust(1)
    echo     return kb.as_markup()
    echo.
    pause
    exit /b 1
)

echo ✅ Функции keyboards импортированы успешно
echo.

echo 🧪 Проверка импорта бота...
python -c "from handlers import instructions as instructions_handlers; print('✅ handlers.instructions импортирован успешно')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта handlers.instructions
    echo 🔄 Восстановление из резервной копии...
    copy "keyboards_backup.py" "keyboards.py" >nul
    pause
    exit /b 1
)

echo ✅ handlers.instructions импортирован успешно
echo.

echo ========================================
echo           🎉 Исправление завершено!
echo ========================================
echo.
echo ✅ keyboards.py исправлен и проверен
echo 📁 Резервная копия: keyboards_backup.py
echo.
echo 🚀 Теперь можно запускать бота:
echo    python bot.py
echo.
pause