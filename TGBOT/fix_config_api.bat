@echo off
echo ========================================
echo    Исправление config.py для API
echo ========================================
echo.

echo 🔧 Создание резервной копии config.py...
if exist "config.py" (
    copy "config.py" "config_backup_api.py" >nul
    echo ✅ Резервная копия создана: config_backup_api.py
) else (
    echo ❌ Файл config.py не найден
    pause
    exit /b 1
)

echo.
echo 🔄 Замена config.py исправленной версией...
if exist "config_fixed_api.py" (
    copy "config_fixed_api.py" "config.py" >nul
    echo ✅ config.py заменен исправленной версией
) else (
    echo ❌ Файл config_fixed_api.py не найден
    echo 🔄 Восстановление из резервной копии...
    copy "config_backup_api.py" "config.py" >nul
    pause
    exit /b 1
)

echo.
echo 🧪 Проверка импорта API_USER_ID...
python -c "from config import API_USER_ID; print('✅ API_USER_ID импортирован:', API_USER_ID)" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта API_USER_ID
    echo 🔄 Восстановление из резервной копии...
    copy "config_backup_api.py" "config.py" >nul
    pause
    exit /b 1
)

echo ✅ API_USER_ID импортирован успешно
echo.

echo 🧪 Проверка импорта api_client...
python -c "from api_client import get_user_by_phone; print('✅ api_client импортирован')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта api_client
    echo 🔄 Восстановление из резервной копии...
    copy "config_backup_api.py" "config.py" >nul
    pause
    exit /b 1
)

echo ✅ api_client импортирован успешно
echo.

echo 🧪 Проверка импорта бота...
python -c "import bot; print('✅ bot.py импортирован')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта bot.py
    echo 🔄 Восстановление из резервной копии...
    copy "config_backup_api.py" "config.py" >nul
    pause
    exit /b 1
)

echo ✅ bot.py импортирован успешно
echo.

echo ========================================
echo           🎉 Исправление завершено!
echo ========================================
echo.
echo ✅ config.py исправлен и проверен
echo ✅ API_USER_ID доступен
echo ✅ api_client работает
echo ✅ bot.py запускается
echo 📁 Резервная копия: config_backup_api.py
echo.
echo 🚀 Теперь можно запускать:
echo    python bot.py
echo.
echo 🧹 Очистка временных файлов...
if exist "config_fixed_api.py" del "config_fixed_api.py"
echo ✅ Временные файлы удалены
echo.
pause