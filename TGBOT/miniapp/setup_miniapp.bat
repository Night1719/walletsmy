@echo off
echo ========================================
echo    Настройка Telegram Mini App
echo ========================================
echo.

echo 🔧 Создание/обновление .env файла...
if not exist ".env" (
    copy .env.example .env
    echo ✅ .env файл создан из шаблона
) else (
    echo ✅ .env файл уже существует
)

echo.
echo 📦 Установка зависимостей...
pip install flask python-dotenv requests

echo.
echo 🧪 Проверка конфигурации...
python -c "from config import MINIAPP_URL, FLASK_PORT; print(f'MINIAPP_URL: {MINIAPP_URL}'); print(f'FLASK_PORT: {FLASK_PORT}')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка загрузки конфигурации
    pause
    exit /b 1
)

echo ✅ Конфигурация загружена успешно
echo.

echo 📝 Настройте следующие параметры в .env файле:
echo    • TELEGRAM_BOT_TOKEN - токен вашего бота
echo    • FLASK_SECRET_KEY - секретный ключ для Flask
echo    • MINIAPP_URL - URL Mini App (https://bot.bunter.ru:4477/miniapp)
echo    • FILE_SERVER_BASE_URL - URL файлового сервера (если используется)
echo.

echo 🚀 Для запуска Mini App выполните:
echo    python run.py
echo.
echo ========================================
echo           🎉 Настройка завершена!
echo ========================================
pause