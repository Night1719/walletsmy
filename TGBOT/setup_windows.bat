@echo off
echo ========================================
echo    Настройка Telegram Bot + Mini App
echo           для Windows
echo ========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден
    echo 📥 Скачайте Python с https://python.org
    echo ⚠️  При установке отметьте "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo ✅ Python найден
echo.

REM Создание виртуального окружения
if not exist "venv" (
    echo 🔧 Создание виртуального окружения...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Ошибка создания виртуального окружения
        pause
        exit /b 1
    )
    echo ✅ Виртуальное окружение создано
) else (
    echo ✅ Виртуальное окружение уже существует
)

echo.
echo 🔧 Активация виртуального окружения...
call venv\Scripts\activate.bat

echo.
echo 📦 Установка зависимостей для бота...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Ошибка установки зависимостей бота
    pause
    exit /b 1
)
echo ✅ Зависимости бота установлены

echo.
echo 📦 Установка зависимостей для Mini App...
cd miniapp
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Ошибка установки зависимостей Mini App
    pause
    exit /b 1
)
echo ✅ Зависимости Mini App установлены
cd ..

echo.
echo 📝 Создание .env файла...
if not exist ".env" (
    echo # === Основные настройки === > .env
    echo TELEGRAM_BOT_TOKEN=your_bot_token_here >> .env
    echo ADMIN_USER_IDS=your_telegram_id >> .env
    echo. >> .env
    echo # === Mini App (ваш домен на порту 4477) === >> .env
    echo MINIAPP_URL=https://your-domain.com:4477/miniapp >> .env
    echo MINIAPP_WEBHOOK_URL=https://your-domain.com:4477 >> .env
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
    echo. >> .env
    echo # === Остальные настройки === >> .env
    echo INTRASERVICE_BASE_URL= >> .env
    echo INTRASERVICE_USER= >> .env
    echo INTRASERVICE_PASS= >> .env
    echo API_USER_ID= >> .env
    echo ✅ .env файл создан
) else (
    echo ✅ .env файл уже существует
)

echo.
echo 📁 Создание папки для инструкций...
if not exist "instructions" (
    mkdir instructions
    echo ✅ Папка instructions создана
) else (
    echo ✅ Папка instructions уже существует
)

echo.
echo 📝 Создание скриптов запуска...

REM Скрипт запуска бота
echo @echo off > start_bot.bat
echo cd /d %~dp0 >> start_bot.bat
echo call venv\Scripts\activate.bat >> start_bot.bat
echo python bot.py >> start_bot.bat
echo pause >> start_bot.bat

REM Скрипт запуска Mini App
echo @echo off > start_miniapp.bat
echo cd /d %~dp0\miniapp >> start_miniapp.bat
echo call ..\venv\Scripts\activate.bat >> start_miniapp.bat
echo python run.py >> start_miniapp.bat
echo pause >> start_miniapp.bat

REM Скрипт запуска с ngrok
echo @echo off > start_with_ngrok.bat
echo cd /d %~dp0 >> start_with_ngrok.bat
echo echo Запуск Mini App... >> start_with_ngrok.bat
echo start "Mini App" cmd /k "start_miniapp.bat" >> start_with_ngrok.bat
echo timeout /t 5 /nobreak ^>nul >> start_with_ngrok.bat
echo echo Запуск ngrok... >> start_with_ngrok.bat
echo echo Установите ngrok с https://ngrok.com/download >> start_with_ngrok.bat
echo echo Распакуйте в C:\ngrok\ >> start_with_ngrok.bat
echo echo Выполните: C:\ngrok\ngrok.exe config add-authtoken YOUR_TOKEN >> start_with_ngrok.bat
echo echo Затем запустите: C:\ngrok\ngrok.exe http 4477 >> start_with_ngrok.bat
echo pause >> start_with_ngrok.bat

echo ✅ Скрипты запуска созданы

echo.
echo ========================================
echo           🎉 Настройка завершена!
echo ========================================
echo.
echo 📋 Следующие шаги:
echo.
echo 1. Отредактируйте файл .env с вашими настройками:
echo    - TELEGRAM_BOT_TOKEN (токен бота)
echo    - ADMIN_USER_IDS (ваш Telegram ID)
echo    - MINIAPP_URL (ваш домен или ngrok URL)
echo    - Настройки SMTP для OTP
echo.
echo 2. Запустите приложение:
echo    - start_miniapp.bat (Mini App)
echo    - start_bot.bat (Бот)
echo    - start_with_ngrok.bat (с ngrok для тестирования)
echo.
echo 3. Протестируйте:
echo    - Mini App: http://localhost:4477/miniapp
echo    - Бот: найдите в Telegram и нажмите /start
echo.
echo 📚 Подробная инструкция: WINDOWS_COMPLETE_SETUP.md
echo.
pause