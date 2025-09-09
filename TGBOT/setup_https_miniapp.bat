@echo off
echo ========================================
echo    Настройка HTTPS Mini App
echo ========================================
echo.

echo 🔧 Создание/обновление .env файла для HTTPS...
if not exist ".env" (
    echo # Mini App Configuration > .env
    echo MINIAPP_URL=https://bot.bunter.ru:4477/miniapp >> .env
    echo MINIAPP_WEBHOOK_URL=https://bot.bunter.ru:4477 >> .env
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
    echo. >> .env
    echo # SSL Configuration >> .env
    echo SSL_VERIFY=true >> .env
    echo SSL_CERT_PATH= >> .env
    echo SSL_KEY_PATH= >> .env
    echo SSL_PASSWORD= >> .env
    echo ✅ .env файл создан с HTTPS настройками
) else (
    echo ✅ .env файл уже существует
    echo.
    echo 🔄 Обновление Mini App URL на HTTPS...
    
    REM Backup current .env
    copy .env .env.backup >nul
    
    REM Update MINIAPP_URL to use HTTPS
    powershell -Command "(Get-Content .env) -replace 'MINIAPP_URL=.*', 'MINIAPP_URL=https://bot.bunter.ru:4477/miniapp' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'MINIAPP_WEBHOOK_URL=.*', 'MINIAPP_WEBHOOK_URL=https://bot.bunter.ru:4477' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'MINIAPP_MODE=.*', 'MINIAPP_MODE=remote' | Set-Content .env"
    
    REM Add SSL configuration if not exists
    findstr /C:"SSL_VERIFY" .env >nul
    if errorlevel 1 (
        echo. >> .env
        echo # SSL Configuration >> .env
        echo SSL_VERIFY=true >> .env
        echo SSL_CERT_PATH= >> .env
        echo SSL_KEY_PATH= >> .env
        echo SSL_PASSWORD= >> .env
    )
    
    echo ✅ Mini App URL обновлен на HTTPS
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

echo 🔍 Проверка SSL соединения...
python -c "import requests; r = requests.get('https://bot.bunter.ru:4477', verify=True, timeout=5); print(f'SSL соединение: OK (статус {r.status_code})')" 2>nul
if errorlevel 1 (
    echo ⚠️  SSL соединение недоступно или сертификат недействителен
    echo 📝 Убедитесь, что:
    echo    1. Сервер bot.bunter.ru:4477 доступен
    echo    2. SSL сертификат настроен правильно
    echo    3. Порт 4477 открыт для HTTPS
) else (
    echo ✅ SSL соединение работает
)

echo.
echo ========================================
echo           🎉 Настройка завершена!
echo ========================================
echo.
echo ✅ Mini App настроен для HTTPS
echo 🔒 URL: https://bot.bunter.ru:4477/miniapp
echo 🔧 Режим: remote
echo 🔐 SSL: включен
echo.
echo 📝 Убедитесь, что:
echo    1. SSL сертификат установлен на сервере
echo    2. Порт 4477 настроен для HTTPS
echo    3. Mini App сервер запущен с SSL
echo    4. Настроены правильные токены в .env
echo.
echo 🔐 Поддерживаемые форматы сертификатов:
echo    • .pem, .crt, .cer - PEM формат (рекомендуется)
echo    • .p12, .pfx - PKCS#12 формат
echo    • .key - приватный ключ (отдельно)
echo.
echo 📁 Пример настройки в .env:
echo    SSL_CERT_PATH=C:\path\to\certificate.pem
echo    SSL_KEY_PATH=C:\path\to\private.key
echo    SSL_PASSWORD=your_password  # только для .p12/.pfx
echo.
echo 🚀 Теперь можно запускать бота:
echo    python bot.py
echo.
pause