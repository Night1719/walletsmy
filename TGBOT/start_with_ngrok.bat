@echo off
echo ========================================
echo    Запуск Mini App с ngrok туннелем
echo ========================================
echo.

REM Проверка наличия ngrok
where ngrok >nul 2>&1
if errorlevel 1 (
    echo ❌ ngrok не найден в PATH
    echo 📥 Скачайте ngrok с https://ngrok.com/download
    echo 📁 Распакуйте в C:\ngrok\
    echo 🔑 Получите токен на https://dashboard.ngrok.com/get-started/your-authtoken
    echo ⚙️  Выполните: C:\ngrok\ngrok.exe config add-authtoken YOUR_TOKEN
    echo.
    pause
    exit /b 1
)

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден
    echo 📥 Установите Python 3.8+ с https://python.org
    pause
    exit /b 1
)

echo ✅ Проверки пройдены
echo.

REM Создание .env файла если не существует
if not exist ".env" (
    echo 📝 Создание .env файла...
    echo # === Основные настройки === > .env
    echo TELEGRAM_BOT_TOKEN=your_bot_token_here >> .env
    echo ADMIN_USER_IDS=your_telegram_id >> .env
    echo. >> .env
    echo # === Mini App (будет обновлен автоматически) === >> .env
    echo MINIAPP_URL=https://your-domain.com/miniapp >> .env
    echo MINIAPP_WEBHOOK_URL=https://your-domain.com >> .env
    echo MINIAPP_MODE=remote >> .env
    echo LINK_EXPIRY_MINUTES=40 >> .env
    echo. >> .env
    echo # === SMTP для OTP === >> .env
    echo SMTP_HOST=smtp.gmail.com >> .env
    echo SMTP_PORT=587 >> .env
    echo SMTP_USER=your_email@gmail.com >> .env
    echo SMTP_PASS=your_app_password >> .env
    echo SMTP_FROM=your_email@gmail.com >> .env
    echo CORP_EMAIL_DOMAIN=yourcompany.com >> .env
    echo.
    echo ⚠️  Отредактируйте .env файл с вашими настройками!
    echo.
    pause
)

echo 🚀 Запуск Mini App...
start "Mini App" cmd /k "cd miniapp && python run.py"

echo ⏳ Ожидание запуска Mini App (5 секунд)...
timeout /t 5 /nobreak >nul

echo 🌐 Запуск ngrok туннеля...
start "ngrok" cmd /k "ngrok http 4477"

echo ⏳ Ожидание запуска ngrok (10 секунд)...
timeout /t 10 /nobreak >nul

echo 📋 Получение URL из ngrok...
for /f "tokens=2" %%i in ('curl -s http://localhost:4040/api/tunnels ^| findstr "public_url"') do (
    set "ngrok_url=%%i"
)

REM Удаление кавычек из URL
set "ngrok_url=%ngrok_url:"=%"

if "%ngrok_url%"=="" (
    echo ❌ Не удалось получить URL из ngrok
    echo 🔍 Проверьте, что ngrok запущен и доступен на http://localhost:4040
    echo.
    pause
    exit /b 1
)

echo ✅ ngrok URL: %ngrok_url%
echo.

REM Обновление .env файла с ngrok URL
echo 🔄 Обновление .env файла...
powershell -Command "(Get-Content .env) -replace 'MINIAPP_URL=.*', 'MINIAPP_URL=%ngrok_url%/miniapp' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'MINIAPP_WEBHOOK_URL=.*', 'MINIAPP_WEBHOOK_URL=%ngrok_url%' | Set-Content .env"

echo ✅ .env файл обновлен
echo.

echo 🤖 Запуск бота...
start "Telegram Bot" cmd /k "python bot.py"

echo.
echo ========================================
echo           🎉 Все сервисы запущены!
echo ========================================
echo.
echo 📱 Mini App: %ngrok_url%/miniapp
echo 🤖 Бот: Запущен в отдельном окне
echo 🌐 ngrok: Запущен в отдельном окне
echo.
echo 📋 Следующие шаги:
echo 1. Отредактируйте .env файл с вашими настройками
echo 2. Перезапустите бота если нужно
echo 3. Протестируйте Mini App в браузере
echo 4. Протестируйте бота в Telegram
echo.
echo ⚠️  Не закрывайте окна ngrok и Mini App!
echo.
pause