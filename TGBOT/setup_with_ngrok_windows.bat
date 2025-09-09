@echo off
echo ========================================
echo    Настройка с ngrok для Windows
echo ========================================
echo.

REM Проверка ngrok
where ngrok >nul 2>&1
if errorlevel 1 (
    echo ❌ ngrok не найден в PATH
    echo.
    echo 📥 Установка ngrok:
    echo 1. Скачайте ngrok с https://ngrok.com/download
    echo 2. Распакуйте в C:\ngrok\
    echo 3. Получите токен на https://dashboard.ngrok.com/get-started/your-authtoken
    echo 4. Выполните: C:\ngrok\ngrok.exe config add-authtoken YOUR_TOKEN
    echo 5. Добавьте C:\ngrok\ в PATH или используйте полный путь
    echo.
    pause
    exit /b 1
)

echo ✅ ngrok найден
echo.

REM Проверка виртуального окружения
if not exist "venv" (
    echo ❌ Виртуальное окружение не найдено
    echo 🔧 Запустите setup_windows.bat для настройки
    pause
    exit /b 1
)

echo ✅ Виртуальное окружение найдено
echo.

echo 🚀 Запуск Mini App...
start "Mini App" cmd /k "cd /d %~dp0\miniapp && ..\venv\Scripts\activate.bat && python run.py"

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
    echo Введите URL вручную:
    set /p ngrok_url="ngrok URL (например: https://abc123.ngrok.io): "
)

echo ✅ ngrok URL: %ngrok_url%
echo.

REM Обновление .env файла с ngrok URL
echo 🔄 Обновление .env файла...
powershell -Command "(Get-Content .env) -replace 'MINIAPP_URL=.*', 'MINIAPP_URL=%ngrok_url%/miniapp' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'MINIAPP_WEBHOOK_URL=.*', 'MINIAPP_WEBHOOK_URL=%ngrok_url%' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'MINIAPP_MODE=.*', 'MINIAPP_MODE=remote' | Set-Content .env"

echo ✅ .env файл обновлен
echo.

echo 🤖 Запуск бота...
start "Telegram Bot" cmd /k "cd /d %~dp0 && venv\Scripts\activate.bat && python bot.py"

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
echo 1. Откройте Mini App в браузере: %ngrok_url%/miniapp
echo 2. Найдите бота в Telegram и нажмите /start
echo 3. Авторизуйтесь и протестируйте инструкции
echo.
echo ⚠️  Не закрывайте окна ngrok, Mini App и Bot!
echo.
pause