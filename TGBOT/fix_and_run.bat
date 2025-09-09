@echo off
echo ========================================
echo    Исправление и запуск Mini App
echo ========================================
echo.

echo 🔧 Исправление config.py...
if exist "config_fixed.py" (
    copy "config_fixed.py" "config.py" >nul
    echo ✅ config.py исправлен
) else (
    echo ❌ Файл config_fixed.py не найден
    echo 📥 Скачайте исправленную версию
    pause
    exit /b 1
)

echo.
echo 🧪 Проверка импорта...
python -c "from config import VIDEO_FILE_EXTENSIONS; print('✅ VIDEO_FILE_EXTENSIONS импортирован успешно')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка импорта VIDEO_FILE_EXTENSIONS
    echo.
    echo 🔧 Ручное исправление...
    echo Добавьте в config.py после строки с SCREENSHOT_KEYWORDS:
    echo VIDEO_FILE_EXTENSIONS = os.getenv("VIDEO_FILE_EXTENSIONS", "mp4,avi,mov,wmv,flv,webm,mkv").split(",")
    echo.
    pause
    exit /b 1
)

echo ✅ Импорт работает корректно
echo.

echo 🚀 Запуск Mini App...
cd miniapp
python run.py