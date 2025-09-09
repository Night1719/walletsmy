@echo off
echo ========================================
echo    Исправление недостающих функций keyboards
echo ========================================
echo.

echo 🔧 Создание резервной копии keyboards.py...
if exist "keyboards.py" (
    copy "keyboards.py" "keyboards_backup_missing.py" >nul
    echo ✅ Резервная копия создана: keyboards_backup_missing.py
) else (
    echo ❌ Файл keyboards.py не найден
    pause
    exit /b 1
)

echo.
echo 🧪 Проверка импорта функций...
python -c "from keyboards import instructions_main_keyboard, instructions_category_keyboard, instruction_keyboard, otp_verification_keyboard, main_menu_after_auth_keyboard; print('✅ Все функции keyboards импортированы')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта функций keyboards
    echo 🔧 Добавление недостающих функций...
    
    REM Добавляем otp_verification_keyboard если его нет
    echo. >> keyboards.py
    echo def otp_verification_keyboard(): >> keyboards.py
    echo     """OTP verification keyboard""" >> keyboards.py
    echo     kb = ReplyKeyboardBuilder() >> keyboards.py
    echo     kb.row(KeyboardButton(text="🔄 Отправить код повторно")) >> keyboards.py
    echo     kb.row(KeyboardButton(text="❌ Отмена")) >> keyboards.py
    echo     return kb.as_markup(resize_keyboard=True) >> keyboards.py
    
    echo ✅ Функции добавлены в keyboards.py
)

echo.
echo 🧪 Повторная проверка импорта функций...
python -c "from keyboards import instructions_main_keyboard, instructions_category_keyboard, instruction_keyboard, otp_verification_keyboard, main_menu_after_auth_keyboard; print('✅ Все функции keyboards импортированы')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта функций keyboards после исправления
    echo 🔄 Восстановление из резервной копии...
    copy "keyboards_backup_missing.py" "keyboards.py" >nul
    pause
    exit /b 1
)

echo ✅ Все функции keyboards импортированы успешно
echo.

echo 🧪 Проверка импорта handlers.instructions...
python -c "from handlers import instructions as instructions_handlers; print('✅ handlers.instructions импортирован')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта handlers.instructions
    echo 🔧 Проверьте файлы handlers/instructions.py и keyboards.py
    pause
    exit /b 1
)

echo ✅ handlers.instructions импортирован успешно
echo.

echo 🧪 Проверка импорта бота...
python -c "import bot; print('✅ bot.py импортирован')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта bot.py
    echo 🔧 Проверьте все зависимости
    pause
    exit /b 1
)

echo ✅ bot.py импортирован успешно
echo.

echo ========================================
echo           🎉 Исправление завершено!
echo ========================================
echo.
echo ✅ keyboards.py исправлен и проверен
echo ✅ handlers.instructions импортирован
echo ✅ bot.py импортирован
echo 📁 Резервная копия: keyboards_backup_missing.py
echo.
echo 🚀 Теперь можно запускать бота:
echo    python bot.py
echo.
pause