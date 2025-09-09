@echo off
echo ========================================
echo    Запуск Telegram Bot + Mini App
echo           для Windows
echo ========================================
echo.

REM Проверка виртуального окружения
if not exist "venv" (
    echo ❌ Виртуальное окружение не найдено
    echo 🔧 Запустите setup_windows.bat для настройки
    pause
    exit /b 1
)

REM Проверка .env файла
if not exist ".env" (
    echo ❌ Файл .env не найден
    echo 🔧 Запустите setup_windows.bat для настройки
    pause
    exit /b 1
)

echo ✅ Проверки пройдены
echo.

echo 🚀 Запуск Mini App...
start "Mini App" cmd /k "cd /d %~dp0\miniapp && ..\venv\Scripts\activate.bat && python run.py"

echo ⏳ Ожидание запуска Mini App (5 секунд)...
timeout /t 5 /nobreak >nul

echo 🤖 Запуск Telegram Bot...
start "Telegram Bot" cmd /k "cd /d %~dp0 && venv\Scripts\activate.bat && python bot.py"

echo.
echo ========================================
echo           🎉 Все сервисы запущены!
echo ========================================
echo.
echo 📱 Mini App: http://localhost:4477/miniapp
echo 🤖 Бот: Запущен в отдельном окне
echo.
echo 📋 Следующие шаги:
echo 1. Откройте Mini App в браузере
echo 2. Найдите бота в Telegram
echo 3. Нажмите /start для авторизации
echo 4. Протестируйте инструкции
echo.
echo ⚠️  Не закрывайте окна Mini App и Bot!
echo.
echo Для остановки закройте все окна или нажмите Ctrl+C
echo.
pause