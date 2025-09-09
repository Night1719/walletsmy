@echo off
echo ========================================
echo    Исправление config.py для Windows
echo ========================================
echo.

echo 🔧 Создание резервной копии config.py...
if exist "config.py" (
    copy "config.py" "config_backup.py" >nul
    echo ✅ Резервная копия создана: config_backup.py
) else (
    echo ❌ Файл config.py не найден
    pause
    exit /b 1
)

echo.
echo 🔄 Замена config.py на исправленную версию...
copy "config_fixed.py" "config.py" >nul
if errorlevel 1 (
    echo ❌ Ошибка замены файла
    pause
    exit /b 1
)

echo ✅ config.py исправлен
echo.

echo 🧪 Проверка импорта...
python -c "from config import VIDEO_FILE_EXTENSIONS; print('✅ VIDEO_FILE_EXTENSIONS импортирован успешно')"
if errorlevel 1 (
    echo ❌ Ошибка импорта
    echo 🔄 Восстановление из резервной копии...
    copy "config_backup.py" "config.py" >nul
    pause
    exit /b 1
)

echo.
echo ========================================
echo           🎉 Исправление завершено!
echo ========================================
echo.
echo ✅ config.py исправлен и проверен
echo 📁 Резервная копия: config_backup.py
echo.
echo 🚀 Теперь можно запускать Mini App:
echo    cd miniapp
echo    python run.py
echo.
pause