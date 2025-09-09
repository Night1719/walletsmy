# ========================================
#    Настройка Telegram Bot + Mini App
#           для Windows
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Настройка Telegram Bot + Mini App" -ForegroundColor Cyan
Write-Host "           для Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка Python
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python найден: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python не найден" -ForegroundColor Red
    Write-Host "📥 Скачайте Python с https://python.org" -ForegroundColor Yellow
    Write-Host "⚠️  При установке отметьте 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host ""

# Создание виртуального окружения
if (-not (Test-Path "venv")) {
    Write-Host "🔧 Создание виртуального окружения..." -ForegroundColor Yellow
    try {
        python -m venv venv
        Write-Host "✅ Виртуальное окружение создано" -ForegroundColor Green
    } catch {
        Write-Host "❌ Ошибка создания виртуального окружения" -ForegroundColor Red
        Read-Host "Нажмите Enter для выхода"
        exit 1
    }
} else {
    Write-Host "✅ Виртуальное окружение уже существует" -ForegroundColor Green
}

Write-Host ""
Write-Host "🔧 Активация виртуального окружения..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "📦 Установка зависимостей для бота..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "✅ Зависимости бота установлены" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка установки зависимостей бота" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host ""
Write-Host "📦 Установка зависимостей для Mini App..." -ForegroundColor Yellow
Set-Location "miniapp"
try {
    pip install -r requirements.txt
    Write-Host "✅ Зависимости Mini App установлены" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка установки зависимостей Mini App" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}
Set-Location ".."

Write-Host ""
Write-Host "📝 Создание .env файла..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    @"
# === Основные настройки ===
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_USER_IDS=your_telegram_id

# === Mini App (ваш домен на порту 4477) ===
MINIAPP_URL=https://your-domain.com:4477/miniapp
MINIAPP_WEBHOOK_URL=https://your-domain.com:4477
MINIAPP_MODE=remote
LINK_EXPIRY_MINUTES=40

# === Поддержка видео ===
ALLOWED_FILE_EXTENSIONS=pdf,docx,doc,txt,mp4,avi,mov,wmv,flv,webm,mkv
MAX_FILE_SIZE_MB=100
VIDEO_FILE_EXTENSIONS=mp4,avi,mov,wmv,flv,webm,mkv

# === SMTP для OTP ===
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
SMTP_FROM=your_email@gmail.com
CORP_EMAIL_DOMAIN=yourcompany.com

# === Остальные настройки ===
INTRASERVICE_BASE_URL=
INTRASERVICE_USER=
INTRASERVICE_PASS=
API_USER_ID=
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ .env файл создан" -ForegroundColor Green
} else {
    Write-Host "✅ .env файл уже существует" -ForegroundColor Green
}

Write-Host ""
Write-Host "📁 Создание папки для инструкций..." -ForegroundColor Yellow
if (-not (Test-Path "instructions")) {
    New-Item -ItemType Directory -Name "instructions" | Out-Null
    Write-Host "✅ Папка instructions создана" -ForegroundColor Green
} else {
    Write-Host "✅ Папка instructions уже существует" -ForegroundColor Green
}

Write-Host ""
Write-Host "📝 Создание скриптов запуска..." -ForegroundColor Yellow

# Скрипт запуска бота
@"
@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
python bot.py
pause
"@ | Out-File -FilePath "start_bot.bat" -Encoding ASCII

# Скрипт запуска Mini App
@"
@echo off
cd /d %~dp0\miniapp
call ..\venv\Scripts\activate.bat
python run.py
pause
"@ | Out-File -FilePath "start_miniapp.bat" -Encoding ASCII

# Скрипт запуска с ngrok
@"
@echo off
cd /d %~dp0
echo Запуск Mini App...
start "Mini App" cmd /k "start_miniapp.bat"
timeout /t 5 /nobreak >nul
echo Запуск ngrok...
echo Установите ngrok с https://ngrok.com/download
echo Распакуйте в C:\ngrok\
echo Выполните: C:\ngrok\ngrok.exe config add-authtoken YOUR_TOKEN
echo Затем запустите: C:\ngrok\ngrok.exe http 4477
pause
"@ | Out-File -FilePath "start_with_ngrok.bat" -Encoding ASCII

Write-Host "✅ Скрипты запуска созданы" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "           🎉 Настройка завершена!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Следующие шаги:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Отредактируйте файл .env с вашими настройками:" -ForegroundColor White
Write-Host "   - TELEGRAM_BOT_TOKEN (токен бота)" -ForegroundColor Gray
Write-Host "   - ADMIN_USER_IDS (ваш Telegram ID)" -ForegroundColor Gray
Write-Host "   - MINIAPP_URL (ваш домен или ngrok URL)" -ForegroundColor Gray
Write-Host "   - Настройки SMTP для OTP" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Запустите приложение:" -ForegroundColor White
Write-Host "   - start_miniapp.bat (Mini App)" -ForegroundColor Gray
Write-Host "   - start_bot.bat (Бот)" -ForegroundColor Gray
Write-Host "   - start_with_ngrok.bat (с ngrok для тестирования)" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Протестируйте:" -ForegroundColor White
Write-Host "   - Mini App: http://localhost:4477/miniapp" -ForegroundColor Gray
Write-Host "   - Бот: найдите в Telegram и нажмите /start" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Подробная инструкция: WINDOWS_COMPLETE_SETUP.md" -ForegroundColor Cyan
Write-Host ""

Read-Host "Нажмите Enter для выхода"