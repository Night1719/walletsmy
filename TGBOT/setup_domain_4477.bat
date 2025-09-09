@echo off
echo ========================================
echo   Настройка Mini App для вашего домена
echo           Порт 4477
echo ========================================
echo.

set /p DOMAIN="Введите ваш домен (например: example.com): "
if "%DOMAIN%"=="" (
    echo ❌ Домен не введен
    pause
    exit /b 1
)

echo.
echo 🔄 Обновление .env файла для домена %DOMAIN%...

REM Создание .env файла если не существует
if not exist ".env" (
    echo 📝 Создание .env файла...
    echo # === Основные настройки === > .env
    echo TELEGRAM_BOT_TOKEN=your_bot_token_here >> .env
    echo ADMIN_USER_IDS=your_telegram_id >> .env
    echo. >> .env
    echo # === Mini App (ваш домен на порту 4477) === >> .env
    echo MINIAPP_URL=https://%DOMAIN%:4477/miniapp >> .env
    echo MINIAPP_WEBHOOK_URL=https://%DOMAIN%:4477 >> .env
    echo MINIAPP_MODE=remote >> .env
    echo LINK_EXPIRY_MINUTES=40 >> .env
    echo. >> .env
    echo # === Поддержка видео === >> .env
    echo ALLOWED_FILE_EXTENSIONS=pdf,docx,doc,txt,mp4,avi,mov,wmv,flv,webm,mkv >> .env
    echo MAX_FILE_SIZE_MB=100 >> .env
    echo VIDEO_FILE_EXTENSIONS=mp4,avi,mov,wmv,flv,webm,mkv >> .env
    echo. >> .env
    echo # === SMTP для OTP === >> .env
    echo SMTP_HOST=smtp.gmail.com >> .env
    echo SMTP_PORT=587 >> .env
    echo SMTP_USER=your_email@gmail.com >> .env
    echo SMTP_PASS=your_app_password >> .env
    echo SMTP_FROM=your_email@gmail.com >> .env
    echo CORP_EMAIL_DOMAIN=yourcompany.com >> .env
) else (
    echo 🔄 Обновление существующего .env файла...
    powershell -Command "(Get-Content .env) -replace 'MINIAPP_URL=.*', 'MINIAPP_URL=https://%DOMAIN%:4477/miniapp' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'MINIAPP_WEBHOOK_URL=.*', 'MINIAPP_WEBHOOK_URL=https://%DOMAIN%:4477' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'MINIAPP_MODE=.*', 'MINIAPP_MODE=remote' | Set-Content .env"
)

echo ✅ .env файл обновлен для домена %DOMAIN%
echo.

echo 📋 Создание Nginx конфигурации...
echo.
echo Создайте файл /etc/nginx/sites-available/miniapp-4477 со следующим содержимым:
echo.
echo server {
echo     listen 443 ssl http2;
echo     server_name %DOMAIN%:4477;
echo.    
echo     # SSL Configuration
echo     ssl_certificate /path/to/your/cert.pem;
echo     ssl_certificate_key /path/to/your/private.key;
echo.    
echo     # Mini App routes
echo     location /miniapp {
echo         proxy_pass http://localhost:4477;
echo         proxy_set_header Host $host;
echo         proxy_set_header X-Real-IP $remote_addr;
echo         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
echo         proxy_set_header X-Forwarded-Proto $scheme;
echo     }
echo.    
echo     # API routes
echo     location /api/ {
echo         proxy_pass http://localhost:4477;
echo         proxy_set_header Host $host;
echo         proxy_set_header X-Real-IP $remote_addr;
echo         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
echo         proxy_set_header X-Forwarded-Proto $scheme;
echo     }
echo }
echo.

echo 📋 Команды для настройки на сервере:
echo.
echo 1. Активация сайта:
echo    sudo ln -s /etc/nginx/sites-available/miniapp-4477 /etc/nginx/sites-enabled/
echo    sudo nginx -t
echo    sudo systemctl reload nginx
echo.
echo 2. SSL сертификат:
echo    sudo certbot --nginx -d %DOMAIN% --nginx-server-root /etc/nginx --nginx-ctl /usr/sbin/nginx
echo.
echo 3. Открытие порта в файрволе:
echo    sudo ufw allow 4477
echo    sudo ufw enable
echo.

echo 🚀 Запуск Mini App локально...
start "Mini App" cmd /k "cd miniapp && python run.py"

echo.
echo ========================================
echo           🎉 Настройка завершена!
echo ========================================
echo.
echo 📱 Mini App URL: https://%DOMAIN%:4477/miniapp
echo 🤖 Бот: Запущен в отдельном окне
echo.
echo 📋 Следующие шаги:
echo 1. Настройте Nginx на сервере (команды выше)
echo 2. Получите SSL сертификат
echo 3. Откройте порт 4477 в файрволе
echo 4. Запустите бота на сервере
echo 5. Протестируйте Mini App
echo.
echo ⚠️  Не закрывайте окно Mini App!
echo.
pause