@echo off
echo ========================================
echo    Быстрая установка SSL сертификата
echo ========================================
echo.

echo 🔐 Выберите способ установки:
echo    1. Интерактивный ввод (рекомендуется)
echo    2. Через файл certificate.txt
echo    3. Отключить SSL верификацию
echo.

set /p choice="Введите номер (1-3): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Запуск интерактивной установки...
    python install_cert_interactive.py
    goto :end
)

if "%choice%"=="2" (
    echo.
    echo 📁 Установка через файл...
    call install_certificate.bat
    goto :end
)

if "%choice%"=="3" (
    echo.
    echo ⚠️  Отключение SSL верификации...
    echo.
    echo 🔧 Обновление .env файла...
    if not exist ".env" (
        copy .env.example .env
    )
    
    powershell -Command "(Get-Content .env) -replace 'SSL_VERIFY=.*', 'SSL_VERIFY=false' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'SSL_VERIFY_CERT=.*', 'SSL_VERIFY_CERT=false' | Set-Content .env"
    powershell -Command "(Get-Content .env) -replace 'SSL_VERIFY_HOSTNAME=.*', 'SSL_VERIFY_HOSTNAME=false' | Set-Content .env"
    
    echo ✅ SSL верификация отключена
    echo.
    echo 🚀 Теперь можно запускать Mini App:
    echo    python run.py
    goto :end
)

echo ❌ Неверный выбор
pause
exit /b 1

:end
echo.
echo ========================================
echo           🎉 Готово!
echo ========================================
pause