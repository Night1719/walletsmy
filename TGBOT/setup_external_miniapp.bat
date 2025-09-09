@echo off
echo ========================================
echo    Настройка внешнего Mini App
echo ========================================
echo.

echo 🔧 Создание/обновление .env файла...
if not exist ".env" (
    echo # Mini App Configuration > .env
    echo MINIAPP_URL=http://bot.bunter.ru:4477/miniapp >> .env
    echo MINIAPP_WEBHOOK_URL=http://bot.bunter.ru:4477 >> .env
    echo MINIAPP_MODE=remote >> .env
    echo LINK_EXPIRY_MINUTES=40 >> .env
    echo. >> .env
    echo # Bot Configuration >> .env
    echo TELEGRAM_BOT_TOKEN=your_bot_token_here >> .env
    echo ADMIN_USER_IDS=your_user_id_here >> .env
    echo. >> .env
    echo # Instructions Configuration >> .env
    echo INSTRUCTIONS_DIR=instructions >> .env
    echo INSTRUCTIONS_CONFIG_FILE=instructions_config.json >> .env
    echo. >> .env
    echo # File Configuration >> .env
    echo VIDEO_FILE_EXTENSIONS=mp4,avi,mov,wmv,flv,webm,mkv >> .env
    echo SCREENSHOT_KEYWORDS=screenshot,screen,shot,скриншот,скрин,снимок >> .env
    echo MAX_FILE_SIZE_MB=100 >> .env
    echo ✅ .env файл создан
) else (
    echo ✅ .env файл уже существует
    echo.
    echo 🔄 Обновление Mini App URL...
    
    REM Backup current .env
    copy .env .env.backup >nul
    
    REM Update MINIAPP_URL to use HTTP instead of HTTPS
    powershell -Command "(Get-Content .env) -replace 'MINIAPP_URL=.*', 'MINIAPP_URL=http://bot.bunter.ru:4477/miniapp' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'MINIAPP_WEBHOOK_URL=.*', 'MINIAPP_WEBHOOK_URL=http://bot.bunter.ru:4477' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'MINIAPP_MODE=.*', 'MINIAPP_MODE=remote' | Set-Content .env"
    
    echo ✅ Mini App URL обновлен на HTTP
)

echo.
echo 🧪 Проверка конфигурации...
python -c "from config import MINIAPP_URL, MINIAPP_MODE; print(f'MINIAPP_URL: {MINIAPP_URL}'); print(f'MINIAPP_MODE: {MINIAPP_MODE}')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка загрузки конфигурации
    echo 🔄 Восстановление из резервной копии...
    if exist ".env.backup" copy .env.backup .env >nul
    pause
    exit /b 1
)

echo ✅ Конфигурация загружена успешно
echo.

echo ========================================
echo           🎉 Настройка завершена!
echo ========================================
echo.
echo ✅ Mini App настроен для внешнего сервера
echo 🌐 URL: http://bot.bunter.ru:4477/miniapp
echo 🔧 Режим: remote
echo.
echo 📝 Убедитесь, что:
echo    1. Сервер bot.bunter.ru:4477 доступен
echo    2. Mini App сервер запущен на внешнем сервере
echo    3. Настроены правильные токены в .env
echo.
echo 🚀 Теперь можно запускать бота:
echo    python bot.py
echo.
pause