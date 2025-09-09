@echo off
echo ========================================
echo    Отключение SSL верификации
echo ========================================
echo.

echo 🔧 Обновление .env файла...
if not exist ".env" (
    echo ❌ .env файл не найден
    echo 📝 Создайте .env файл из .env.example
    pause
    exit /b 1
)

echo ✅ .env файл найден

echo.
echo 🔄 Отключение SSL верификации...

REM Backup current .env
copy .env .env.backup >nul

REM Update SSL settings
powershell -Command "(Get-Content .env) -replace 'SSL_VERIFY=.*', 'SSL_VERIFY=false' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'SSL_VERIFY_CERT=.*', 'SSL_VERIFY_CERT=false' | Set-Content .env"
powershell -Command "(Get-Content .env) -replace 'SSL_VERIFY_HOSTNAME=.*', 'SSL_VERIFY_HOSTNAME=false' | Set-Content .env"

REM Add SSL settings if they don't exist
findstr /C:"SSL_VERIFY" .env >nul
if errorlevel 1 (
    echo. >> .env
    echo # SSL Configuration >> .env
    echo SSL_VERIFY=false >> .env
    echo SSL_VERIFY_CERT=false >> .env
    echo SSL_VERIFY_HOSTNAME=false >> .env
)

echo ✅ SSL верификация отключена
echo.

echo 🧪 Проверка конфигурации...
python -c "from config import SSL_VERIFY, SSL_VERIFY_CERT, SSL_VERIFY_HOSTNAME; print(f'SSL_VERIFY: {SSL_VERIFY}'); print(f'SSL_VERIFY_CERT: {SSL_VERIFY_CERT}'); print(f'SSL_VERIFY_HOSTNAME: {SSL_VERIFY_HOSTNAME}')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка загрузки конфигурации
    echo 🔄 Восстановление из резервной копии...
    if exist ".env.backup" copy .env.backup .env >nul
    pause
    exit /b 1
)

echo ✅ Конфигурация обновлена успешно
echo.

echo 🚀 Теперь можно запускать бота:
echo    python bot.py
echo.

echo ⚠️  ВНИМАНИЕ: SSL верификация отключена!
echo    Это означает, что соединения не будут проверяться на безопасность.
echo    Используйте только в доверенной сети!
echo.

pause