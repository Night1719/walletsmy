@echo off
echo ========================================
echo    Полная замена keyboards.py
echo ========================================
echo.

echo 🔧 Создание резервной копии keyboards.py...
if exist "keyboards.py" (
    copy "keyboards.py" "keyboards_backup_complete.py" >nul
    echo ✅ Резервная копия создана: keyboards_backup_complete.py
) else (
    echo ❌ Файл keyboards.py не найден
    pause
    exit /b 1
)

echo.
echo 🔄 Замена keyboards.py полной версией...
if exist "keyboards_complete.py" (
    copy "keyboards_complete.py" "keyboards.py" >nul
    echo ✅ keyboards.py заменен полной версией
) else (
    echo ❌ Файл keyboards_complete.py не найден
    echo 🔄 Восстановление из резервной копии...
    copy "keyboards_backup_complete.py" "keyboards.py" >nul
    pause
    exit /b 1
)

echo.
echo 🧪 Проверка синтаксиса keyboards.py...
python -c "import keyboards; print('✅ keyboards.py синтаксически корректен')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка синтаксиса в keyboards.py
    echo 🔄 Восстановление из резервной копии...
    copy "keyboards_backup_complete.py" "keyboards.py" >nul
    echo ❌ Не удалось исправить keyboards.py
    pause
    exit /b 1
)

echo ✅ keyboards.py синтаксически корректен
echo.

echo 🧪 Проверка импорта всех функций...
python -c "from keyboards import instructions_main_keyboard, instructions_category_keyboard, instruction_keyboard, otp_verification_keyboard, main_menu_after_auth_keyboard; print('✅ Все функции keyboards импортированы')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта функций keyboards
    echo 🔄 Восстановление из резервной копии...
    copy "keyboards_backup_complete.py" "keyboards.py" >nul
    pause
    exit /b 1
)

echo ✅ Все функции keyboards импортированы успешно
echo.

echo 🧪 Проверка импорта handlers.instructions...
python -c "from handlers import instructions as instructions_handlers; print('✅ handlers.instructions импортирован')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта handlers.instructions
    echo 🔄 Восстановление из резервной копии...
    copy "keyboards_backup_complete.py" "keyboards.py" >nul
    pause
    exit /b 1
)

echo ✅ handlers.instructions импортирован успешно
echo.

echo 🧪 Проверка импорта бота...
python -c "import bot; print('✅ bot.py импортирован')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта bot.py
    echo 🔄 Восстановление из резервной копии...
    copy "keyboards_backup_complete.py" "keyboards.py" >nul
    pause
    exit /b 1
)

echo ✅ bot.py импортирован успешно
echo.

echo ========================================
echo           🎉 Замена завершена!
echo ========================================
echo.
echo ✅ keyboards.py заменен полной версией
echo ✅ Все функции импортированы
echo ✅ handlers.instructions работает
echo ✅ bot.py работает
echo 📁 Резервная копия: keyboards_backup_complete.py
echo.
echo 🚀 Теперь можно запускать бота:
echo    python bot.py
echo.
echo 🧹 Очистка временных файлов...
if exist "keyboards_complete.py" del "keyboards_complete.py"
if exist "keyboards_fixed.py" del "keyboards_fixed.py"
echo ✅ Временные файлы удалены
echo.
pause