@echo off
echo ========================================
echo    Исправление отступов keyboards.py
echo ========================================
echo.

echo 🔧 Создание резервной копии keyboards.py...
if exist "keyboards.py" (
    copy "keyboards.py" "keyboards_backup_indent.py" >nul
    echo ✅ Резервная копия создана: keyboards_backup_indent.py
) else (
    echo ❌ Файл keyboards.py не найден
    pause
    exit /b 1
)

echo.
echo 🔄 Замена keyboards.py исправленной версией...
if exist "keyboards_fixed.py" (
    copy "keyboards_fixed.py" "keyboards.py" >nul
    echo ✅ keyboards.py заменен исправленной версией
) else (
    echo ❌ Файл keyboards_fixed.py не найден
    echo 🔄 Восстановление из резервной копии...
    copy "keyboards_backup_indent.py" "keyboards.py" >nul
    pause
    exit /b 1
)

echo.
echo 🧪 Проверка синтаксиса keyboards.py...
python -c "import keyboards; print('✅ keyboards.py синтаксически корректен')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка синтаксиса в keyboards.py
    echo 🔄 Восстановление из резервной копии...
    copy "keyboards_backup_indent.py" "keyboards.py" >nul
    echo ❌ Не удалось исправить keyboards.py
    pause
    exit /b 1
)

echo ✅ keyboards.py синтаксически корректен
echo.

echo 🧪 Проверка импорта функций...
python -c "from keyboards import instructions_category_keyboard, instruction_keyboard; print('✅ Функции keyboards импортированы')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта функций keyboards
    echo 🔄 Восстановление из резервной копии...
    copy "keyboards_backup_indent.py" "keyboards.py" >nul
    pause
    exit /b 1
)

echo ✅ Функции keyboards импортированы успешно
echo.

echo 🧪 Проверка импорта бота...
python -c "from handlers import instructions as instructions_handlers; print('✅ handlers.instructions импортирован')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта handlers.instructions
    echo 🔄 Восстановление из резервной копии...
    copy "keyboards_backup_indent.py" "keyboards.py" >nul
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
echo 📁 Резервная копия: keyboards_backup_indent.py
echo.
echo 🚀 Теперь можно запускать бота:
echo    python bot.py
echo.
pause