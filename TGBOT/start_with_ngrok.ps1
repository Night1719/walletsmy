# ========================================
#    Запуск Mini App с ngrok туннелем
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Запуск Mini App с ngrok туннелем" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка наличия ngrok
try {
    $ngrokVersion = ngrok version 2>$null
    Write-Host "✅ ngrok найден: $ngrokVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ngrok не найден в PATH" -ForegroundColor Red
    Write-Host "📥 Скачайте ngrok с https://ngrok.com/download" -ForegroundColor Yellow
    Write-Host "📁 Распакуйте в C:\ngrok\" -ForegroundColor Yellow
    Write-Host "🔑 Получите токен на https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor Yellow
    Write-Host "⚙️  Выполните: C:\ngrok\ngrok.exe config add-authtoken YOUR_TOKEN" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

# Проверка наличия Python
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python найден: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python не найден" -ForegroundColor Red
    Write-Host "📥 Установите Python 3.8+ с https://python.org" -ForegroundColor Yellow
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host "✅ Проверки пройдены" -ForegroundColor Green
Write-Host ""

# Создание .env файла если не существует
if (-not (Test-Path ".env")) {
    Write-Host "📝 Создание .env файла..." -ForegroundColor Yellow
    @"
# === Основные настройки ===
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_USER_IDS=your_telegram_id

# === Mini App (будет обновлен автоматически) ===
MINIAPP_URL=https://your-domain.com/miniapp
MINIAPP_WEBHOOK_URL=https://your-domain.com
MINIAPP_MODE=remote
LINK_EXPIRY_MINUTES=40

# === SMTP для OTP ===
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
SMTP_FROM=your_email@gmail.com
CORP_EMAIL_DOMAIN=yourcompany.com
"@ | Out-File -FilePath ".env" -Encoding UTF8
    
    Write-Host "⚠️  Отредактируйте .env файл с вашими настройками!" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Нажмите Enter для продолжения"
}

Write-Host "🚀 Запуск Mini App..." -ForegroundColor Green
Start-Process -FilePath "cmd" -ArgumentList "/k", "cd miniapp && python run.py" -WindowStyle Normal

Write-Host "⏳ Ожидание запуска Mini App (5 секунд)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "🌐 Запуск ngrok туннеля..." -ForegroundColor Green
Start-Process -FilePath "ngrok" -ArgumentList "http", "4477" -WindowStyle Normal

Write-Host "⏳ Ожидание запуска ngrok (10 секунд)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "📋 Получение URL из ngrok..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -Method Get
    $ngrokUrl = $response.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1 -ExpandProperty public_url
    
    if (-not $ngrokUrl) {
        throw "No HTTPS tunnel found"
    }
    
    Write-Host "✅ ngrok URL: $ngrokUrl" -ForegroundColor Green
    Write-Host ""
    
    # Обновление .env файла с ngrok URL
    Write-Host "🔄 Обновление .env файла..." -ForegroundColor Yellow
    $envContent = Get-Content ".env"
    $envContent = $envContent -replace "MINIAPP_URL=.*", "MINIAPP_URL=$ngrokUrl/miniapp"
    $envContent = $envContent -replace "MINIAPP_WEBHOOK_URL=.*", "MINIAPP_WEBHOOK_URL=$ngrokUrl"
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    
    Write-Host "✅ .env файл обновлен" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "🤖 Запуск бота..." -ForegroundColor Green
    Start-Process -FilePath "cmd" -ArgumentList "/k", "python bot.py" -WindowStyle Normal
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "           🎉 Все сервисы запущены!" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📱 Mini App: $ngrokUrl/miniapp" -ForegroundColor Cyan
    Write-Host "🤖 Бот: Запущен в отдельном окне" -ForegroundColor Green
    Write-Host "🌐 ngrok: Запущен в отдельном окне" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Следующие шаги:" -ForegroundColor Yellow
    Write-Host "1. Отредактируйте .env файл с вашими настройками" -ForegroundColor White
    Write-Host "2. Перезапустите бота если нужно" -ForegroundColor White
    Write-Host "3. Протестируйте Mini App в браузере" -ForegroundColor White
    Write-Host "4. Протестируйте бота в Telegram" -ForegroundColor White
    Write-Host ""
    Write-Host "⚠️  Не закрывайте окна ngrok и Mini App!" -ForegroundColor Red
    Write-Host ""
    
} catch {
    Write-Host "❌ Не удалось получить URL из ngrok" -ForegroundColor Red
    Write-Host "🔍 Проверьте, что ngrok запущен и доступен на http://localhost:4040" -ForegroundColor Yellow
    Write-Host "Ошибка: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Read-Host "Нажмите Enter для выхода"