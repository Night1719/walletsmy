# ========================================
#    Исправление config.py для Windows
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Исправление config.py для Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔧 Создание резервной копии config.py..." -ForegroundColor Yellow
if (Test-Path "config.py") {
    Copy-Item "config.py" "config_backup.py" -Force
    Write-Host "✅ Резервная копия создана: config_backup.py" -ForegroundColor Green
} else {
    Write-Host "❌ Файл config.py не найден" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host ""
Write-Host "🔄 Замена config.py на исправленную версию..." -ForegroundColor Yellow
try {
    Copy-Item "config_fixed.py" "config.py" -Force
    Write-Host "✅ config.py исправлен" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка замены файла" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host ""
Write-Host "🧪 Проверка импорта..." -ForegroundColor Yellow
try {
    python -c "from config import VIDEO_FILE_EXTENSIONS; print('✅ VIDEO_FILE_EXTENSIONS импортирован успешно')"
    Write-Host "✅ Импорт работает корректно" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка импорта" -ForegroundColor Red
    Write-Host "🔄 Восстановление из резервной копии..." -ForegroundColor Yellow
    Copy-Item "config_backup.py" "config.py" -Force
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "           🎉 Исправление завершено!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ config.py исправлен и проверен" -ForegroundColor Green
Write-Host "📁 Резервная копия: config_backup.py" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 Теперь можно запускать Mini App:" -ForegroundColor Yellow
Write-Host "   cd miniapp" -ForegroundColor Gray
Write-Host "   python run.py" -ForegroundColor Gray
Write-Host ""

Read-Host "Нажмите Enter для выхода"