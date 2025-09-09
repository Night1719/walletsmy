@echo off
echo ========================================
echo    Добавление otp_verification_keyboard
echo ========================================
echo.

echo 🔧 Создание резервной копии...
if exist "keyboards.py" (
    copy "keyboards.py" "keyboards_backup_otp.py" >nul
    echo ✅ Резервная копия создана
) else (
    echo ❌ Файл keyboards.py не найден
    pause
    exit /b 1
)

echo.
echo 🔍 Проверка наличия otp_verification_keyboard...
findstr /C:"def otp_verification_keyboard" keyboards.py >nul
if not errorlevel 1 (
    echo ✅ Функция otp_verification_keyboard уже существует
    goto :test_import
)

echo.
echo ➕ Добавление otp_verification_keyboard...

REM Добавляем функцию в конец файла
echo. >> keyboards.py
echo def otp_verification_keyboard(): >> keyboards.py
echo     """OTP verification keyboard""" >> keyboards.py
echo     kb = ReplyKeyboardBuilder() >> keyboards.py
echo     kb.row(KeyboardButton(text="🔄 Отправить код повторно")) >> keyboards_new.py
echo     kb.row(KeyboardButton(text="❌ Отмена")) >> keyboards_new.py
echo     return kb.as_markup(resize_keyboard=True) >> keyboards.py

echo ✅ Функция добавлена

:test_import
echo.
echo 🧪 Проверка импорта...
python -c "from keyboards import otp_verification_keyboard; print('✅ otp_verification_keyboard импортирован')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта otp_verification_keyboard
    echo 🔄 Восстановление из резервной копии...
    copy "keyboards_backup_otp.py" "keyboards.py" >nul
    pause
    exit /b 1
)

echo ✅ otp_verification_keyboard импортирован успешно
echo.

echo 🧪 Проверка импорта всех функций...
python -c "from keyboards import instructions_main_keyboard, instructions_category_keyboard, instruction_keyboard, otp_verification_keyboard, main_menu_after_auth_keyboard; print('✅ Все функции импортированы')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта всех функций
    echo 🔄 Восстановление из резервной копии...
    copy "keyboards_backup_otp.py" "keyboards.py" >nul
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
    copy "keyboards_backup_otp.py" "keyboards.py" >nul
    pause
    exit /b 1
)

echo ✅ bot.py импортирован успешно
echo.

echo ========================================
echo           🎉 Исправление завершено!
echo ========================================
echo.
echo ✅ otp_verification_keyboard добавлен
echo ✅ Все функции работают
echo ✅ bot.py запускается
echo 📁 Резервная копия: keyboards_backup_otp.py
echo.
echo 🚀 Теперь можно запускать:
echo    python bot.py
echo.
pause