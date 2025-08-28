@echo off
chcp 65001 >nul
title BG Survey Platform - BunterGroup

echo.
echo ========================================
echo    BG Survey Platform v1.0.0
echo    BunterGroup
echo ========================================
echo.

echo [INFO] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python не установлен или не найден в PATH
    echo [INFO] Пожалуйста, установите Python 3.8+ с https://python.org
    pause
    exit /b 1
)

echo [INFO] Python найден
python --version

echo.
echo [INFO] Проверка виртуального окружения...
if not exist "venv" (
    echo [INFO] Создание виртуального окружения...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Не удалось создать виртуальное окружение
        pause
        exit /b 1
    )
    echo [SUCCESS] Виртуальное окружение создано
) else (
    echo [INFO] Виртуальное окружение уже существует
)

echo.
echo [INFO] Активация виртуального окружения...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Не удалось активировать виртуальное окружение
    pause
    exit /b 1
)

echo.
echo [INFO] Проверка зависимостей...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [INFO] Установка зависимостей...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Не удалось установить зависимости
        pause
        exit /b 1
    )
    echo [SUCCESS] Зависимости установлены
) else (
    echo [INFO] Зависимости уже установлены
)

echo.
echo [INFO] Проверка базы данных...
if not exist "surveys.db" (
    echo [INFO] База данных не найдена, будет создана автоматически
)

echo.
echo [INFO] Запуск BG Survey Platform...
echo [INFO] Приложение будет доступно по адресу: http://localhost:5000
echo [INFO] Для остановки нажмите Ctrl+C
echo.

python app.py

echo.
echo [INFO] Приложение остановлено
pause