@echo off
echo ========================================
echo    Установка SSL сертификата
echo ========================================
echo.

echo 🔐 Этот скрипт поможет установить SSL сертификат для Mini App
echo.

echo 📋 Создание файла для ввода сертификата...
echo.

REM Create input file
echo Вставьте ваш SSL сертификат в файл certificate.txt
echo (включая -----BEGIN CERTIFICATE----- и -----END CERTIFICATE-----)
echo.
echo После вставки сохраните файл и нажмите любую клавишу...
echo.

if not exist "certificate.txt" (
    echo. > certificate.txt
    echo Файл certificate.txt создан
    echo Откройте его в блокноте и вставьте сертификат
    echo.
    notepad certificate.txt
    echo.
    echo Нажмите любую клавишу после сохранения файла...
    pause >nul
)

echo.
echo 🔍 Проверка файла сертификата...
if not exist "certificate.txt" (
    echo ❌ Файл certificate.txt не найден
    pause
    exit /b 1
)

REM Check if certificate file has content
findstr /C:"-----BEGIN CERTIFICATE-----" certificate.txt >nul
if errorlevel 1 (
    echo ❌ Файл certificate.txt не содержит сертификат
    echo 📝 Убедитесь, что вы вставили сертификат в правильном формате
    pause
    exit /b 1
)

echo ✅ Сертификат найден в файле

echo.
echo 📁 Создание директории для сертификатов...
if not exist "certificates" mkdir certificates

echo.
echo 📋 Копирование сертификата...
copy certificate.txt certificates\server.crt >nul
echo ✅ Сертификат скопирован в certificates\server.crt

echo.
echo 🔧 Обновление .env файла...
if not exist ".env" (
    copy .env.example .env
    echo ✅ .env файл создан из шаблона
)

REM Update .env with certificate path
powershell -Command "(Get-Content .env) -replace 'SSL_CERT_PATH=.*', 'SSL_CERT_PATH=certificates\\server.crt' | Set-Content .env"

REM Add SSL settings if they don't exist
findstr /C:"SSL_VERIFY" .env >nul
if errorlevel 1 (
    echo. >> .env
    echo # SSL Configuration >> .env
    echo SSL_VERIFY=true >> .env
    echo SSL_VERIFY_CERT=true >> .env
    echo SSL_VERIFY_HOSTNAME=true >> .env
    echo SSL_CERT_PATH=certificates\server.crt >> .env
)

echo ✅ .env файл обновлен

echo.
echo 🧪 Проверка конфигурации...
python -c "from config import SSL_CERT_PATH; print(f'SSL_CERT_PATH: {SSL_CERT_PATH}')" 2>nul
if errorlevel 1 (
    echo ❌ Ошибка загрузки конфигурации
    pause
    exit /b 1
)

echo ✅ Конфигурация загружена успешно

echo.
echo ========================================
echo           🎉 Установка завершена!
echo ========================================
echo.

echo 📁 Файлы созданы:
echo    certificates\server.crt - SSL сертификат
echo    .env - обновлен с путем к сертификату
echo.

echo 🚀 Теперь можно запускать Mini App с SSL:
echo    python run.py
echo    или
echo    run_ssl.bat
echo.

echo 🗑️  Можно удалить временный файл:
echo    del certificate.txt
echo.

pause