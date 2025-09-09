@echo off
echo ========================================
echo    Запуск Mini App с SSL
echo ========================================
echo.

echo 🔧 Проверка конфигурации...
if not exist ".env" (
    echo ❌ .env файл не найден
    echo 📝 Создайте .env файл из .env.example
    pause
    exit /b 1
)

echo ✅ .env файл найден

echo.
echo 🔐 Настройка SSL...
set USE_SSL=true
set FLASK_DEBUG=false

echo.
echo 🚀 Запуск Mini App с SSL...
echo 📍 URL: https://bot.bunter.ru:4477
echo 🔒 SSL: включен
echo.

python run.py

pause