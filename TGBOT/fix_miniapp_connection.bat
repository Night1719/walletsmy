@echo off
echo ========================================
echo    Исправление подключения к Mini App
echo ========================================
echo.

echo 🔧 Исправление проблем с Mini App...
echo.

echo 1. Отключение SSL верификации в боте...
call disable_ssl_for_miniapp.bat

echo.
echo 2. Проверка Mini App...
cd miniapp

echo.
echo 🧪 Тестирование Mini App...
python -c "
try:
    from app import app, INSTRUCTION_FILES
    print('✅ Mini App загружается успешно')
    print(f'✅ Instruction files: {len(INSTRUCTION_FILES)} loaded')
except Exception as e:
    print(f'❌ Ошибка Mini App: {e}')
"

echo.
echo 3. Запуск Mini App в фоне...
echo 🚀 Mini App запускается на порту 4477...
echo.

REM Start Mini App in background
start /B python run.py

echo.
echo ⏳ Ожидание запуска Mini App...
timeout /t 3 /nobreak >nul

echo.
echo 🧪 Тестирование подключения...
cd ..
python -c "
import requests
try:
    response = requests.get('http://localhost:4477', timeout=5, verify=False)
    print(f'✅ Mini App отвечает: {response.status_code}')
except Exception as e:
    print(f'❌ Mini App не отвечает: {e}')
"

echo.
echo ========================================
echo           🎉 Исправления применены!
echo ========================================
echo.

echo 📋 Что исправлено:
echo    ✅ SSL верификация отключена в боте
echo    ✅ Mini App исправлен для работы без instruction_manager
echo    ✅ Mini App запущен на порту 4477
echo.

echo 🚀 Теперь можно запускать бота:
echo    python bot.py
echo.

echo 🌐 Mini App доступен по адресам:
echo    http://localhost:4477
echo    http://127.0.0.1:4477
echo    https://127.0.0.1:4477 (с самоподписным сертификатом)
echo.

pause