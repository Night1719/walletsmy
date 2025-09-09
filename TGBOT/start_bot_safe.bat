@echo off
echo ========================================
echo    Безопасный запуск бота
echo ========================================
echo.

echo 🔍 Проверка запущенных процессов Python...
tasklist | findstr python.exe >nul
if not errorlevel 1 (
    echo ⚠️  Найдены запущенные процессы Python
    echo.
    echo Остановка всех процессов Python...
    taskkill /f /im python.exe >nul 2>&1
    taskkill /f /im python3.exe >nul 2>&1
    echo ✅ Процессы остановлены
    echo.
    echo ⏳ Ожидание 3 секунды...
    timeout /t 3 /nobreak >nul
) else (
    echo ✅ Процессы Python не найдены
)

echo.
echo 🚀 Запуск бота...
python bot.py

echo.
echo Бот остановлен. Нажмите любую клавишу для выхода...
pause >nul