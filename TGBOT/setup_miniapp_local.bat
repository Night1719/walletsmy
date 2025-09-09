@echo off
echo ========================================
echo    Настройка Mini App для локального использования
echo ========================================
echo.

echo 🔧 Создание .env файла для Mini App...
if not exist ".env" (
    echo # Mini App Configuration > .env
    echo MINIAPP_URL=http://localhost:4477/miniapp >> .env
    echo MINIAPP_WEBHOOK_URL=http://localhost:4477 >> .env
    echo MINIAPP_MODE=local >> .env
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
)

echo.
echo 🚀 Запуск Mini App...
cd miniapp
if exist "run.py" (
    echo Запуск Mini App на порту 4477...
    python run.py
) else (
    echo ❌ Файл miniapp/run.py не найден
    echo Создание простого Mini App сервера...
    
    echo from flask import Flask, render_template, request, jsonify > app.py
    echo import os >> app.py
    echo import time >> app.py
    echo. >> app.py
    echo app = Flask(__name__) >> app.py
    echo. >> app.py
    echo @app.route('/') >> app.py
    echo def index(): >> app.py
    echo     return "Mini App Server Running" >> app.py
    echo. >> app.py
    echo @app.route('/miniapp') >> app.py
    echo def miniapp(): >> app.py
    echo     return render_template('index.html') >> app.py
    echo. >> app.py
    echo @app.route('/secure/<token>') >> app.py
    echo def secure_viewer(token): >> app.py
    echo     return render_template('secure_viewer.html', token=token) >> app.py
    echo. >> app.py
    echo if __name__ == '__main__': >> app.py
    echo     app.run(host='0.0.0.0', port=4477, debug=True) >> app.py
    
    echo ✅ Простой Mini App сервер создан
    echo Запуск...
    python app.py
)

echo.
echo ========================================
echo           🎉 Настройка завершена!
echo ========================================
echo.
echo ✅ Mini App настроен для локального использования
echo 🌐 URL: http://localhost:4477/miniapp
echo.
echo 📝 Не забудьте:
echo    1. Настроить .env файл с вашими токенами
echo    2. Запустить Mini App: cd miniapp && python run.py
echo    3. Запустить бота: python bot.py
echo.
pause