@echo off
echo ========================================
echo    Исправление всех ошибок для Windows
echo ========================================
echo.

echo 🔧 Исправление config.py...
if exist "config_fixed.py" (
    copy "config_fixed.py" "config.py" >nul
    echo ✅ config.py исправлен
) else (
    echo ❌ Файл config_fixed.py не найден
    echo 📝 Создание исправленного config.py...
    
    REM Создаем исправленный config.py
    echo # Video file extensions > temp_config.py
    echo VIDEO_FILE_EXTENSIONS = os.getenv("VIDEO_FILE_EXTENSIONS", "mp4,avi,mov,wmv,flv,webm,mkv").split(",") >> temp_config.py
    
    REM Добавляем к существующему config.py
    type config.py >> temp_config.py
    move temp_config.py config.py >nul
    echo ✅ config.py исправлен вручную
)

echo.
echo 🧪 Проверка config.py...
python -c "from config import VIDEO_FILE_EXTENSIONS; print('✅ VIDEO_FILE_EXTENSIONS импортирован')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка в config.py
    echo 🔧 Ручное исправление config.py...
    echo Добавьте в конец config.py:
    echo VIDEO_FILE_EXTENSIONS = os.getenv("VIDEO_FILE_EXTENSIONS", "mp4,avi,mov,wmv,flv,webm,mkv").split(",")
    pause
    exit /b 1
)

echo ✅ config.py работает корректно
echo.

echo 🔧 Проверка keyboards.py...
python -c "from keyboards import instructions_category_keyboard, instruction_keyboard; print('✅ keyboards функции импортированы')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка в keyboards.py
    echo 🔧 Добавление недостающих функций...
    
    REM Добавляем недостающие функции в keyboards.py
    echo. >> keyboards.py
    echo def instructions_category_keyboard(category_id: str): >> keyboards.py
    echo     kb = InlineKeyboardBuilder() >> keyboards.py
    echo     manager = get_instruction_manager() >> keyboards.py
    echo     instructions = manager.get_instructions_by_category(category_id) >> keyboards.py
    echo     if instructions: >> keyboards.py
    echo         for instruction in instructions: >> keyboards.py
    echo             kb.button(text=f"📄 {instruction['name']}", callback_data=f"instruction_{category_id}_{instruction['id']}") >> keyboards.py
    echo     else: >> keyboards.py
    echo         kb.button(text="❌ Инструкции не найдены", callback_data="no_instructions") >> keyboards.py
    echo     kb.button(text="⬅️ Назад", callback_data="back_to_categories") >> keyboards.py
    echo     kb.adjust(1) >> keyboards.py
    echo     return kb.as_markup() >> keyboards.py
    echo. >> keyboards.py
    echo def instruction_keyboard(category_id: str, instruction_id: str): >> keyboards.py
    echo     kb = InlineKeyboardBuilder() >> keyboards.py
    echo     manager = get_instruction_manager() >> keyboards.py
    echo     instruction = manager.get_instruction(category_id, instruction_id) >> keyboards.py
    echo     if instruction: >> keyboards.py
    echo         for format_type in instruction.get('formats', []): >> keyboards.py
    echo             kb.button(text=f"📄 {format_type.upper()}", callback_data=f"create_secure_link_{category_id}_{instruction_id}_{format_type}") >> keyboards.py
    echo     kb.button(text="⬅️ Назад", callback_data=f"category_{category_id}") >> keyboards.py
    echo     kb.adjust(1) >> keyboards.py
    echo     return kb.as_markup() >> keyboards.py
    
    echo ✅ Функции добавлены в keyboards.py
)

echo.
echo 🧪 Проверка импорта бота...
python -c "from handlers import instructions as instructions_handlers; print('✅ handlers.instructions импортирован')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта handlers.instructions
    echo 🔧 Проверьте файлы handlers/instructions.py и keyboards.py
    pause
    exit /b 1
)

echo ✅ handlers.instructions импортирован успешно
echo.

echo ========================================
echo           🎉 Все ошибки исправлены!
echo ========================================
echo.
echo ✅ config.py исправлен
echo ✅ keyboards.py исправлен
echo ✅ handlers.instructions импортирован
echo.
echo 🚀 Теперь можно запускать:
echo    python bot.py
echo.
echo 📱 Mini App:
echo    cd miniapp
echo    python run.py
echo.
pause