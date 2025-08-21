@echo off
chcp 65001 >nul
echo ========================================
echo    BG Опросник - Запуск на Windows
echo ========================================
echo.

REM Проверяем наличие Python
echo [1/8] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден!
    echo Установите Python с https://python.org
    pause
    exit /b 1
)
echo ✓ Python найден

REM Проверяем наличие pip
echo [2/8] Проверка pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: pip не найден!
    pause
    exit /b 1
)
echo ✓ pip найден

REM Создаем виртуальное окружение
echo [3/8] Создание виртуального окружения...
if not exist "venv" (
    python -m venv venv
    if errorlevel 1 (
        echo ОШИБКА: Не удалось создать виртуальное окружение!
        pause
        exit /b 1
    )
    echo ✓ Виртуальное окружение создано
) else (
    echo ✓ Виртуальное окружение уже существует
)

REM Активируем виртуальное окружение
echo [4/8] Активация виртуального окружения...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ОШИБКА: Не удалось активировать виртуальное окружение!
    pause
    exit /b 1
)
echo ✓ Виртуальное окружение активировано

REM Обновляем pip
echo [5/8] Обновление pip...
python -m pip install --upgrade pip
echo ✓ pip обновлен

REM Устанавливаем зависимости
echo [6/8] Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo ОШИБКА: Не удалось установить зависимости!
    pause
    exit /b 1
)
echo ✓ Зависимости установлены

REM Создаем необходимые директории
echo [7/8] Создание директорий...
if not exist "staticfiles" mkdir staticfiles
if not exist "media" mkdir media
echo ✓ Директории созданы

REM Проверяем наличие manage.py
echo [8/8] Проверка Django проекта...
if not exist "manage.py" (
    echo ОШИБКА: Файл manage.py не найден!
    echo Убедитесь, что вы находитесь в корневой папке проекта
    pause
    exit /b 1
)
echo ✓ manage.py найден

REM Создаем миграции
echo.
echo ========================================
echo    Создание миграций базы данных...
echo ========================================
python manage.py makemigrations users
python manage.py makemigrations surveys

REM Применяем миграции
echo.
echo ========================================
echo    Применение миграций...
echo ========================================
python manage.py migrate

REM Создаем суперпользователя
echo.
echo ========================================
echo    Создание администратора...
echo ========================================
echo Создаем суперпользователя admin/admin123...
echo from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None; user = User.objects.get(username='admin'); user.role = 'admin'; user.can_create_surveys = True; user.save() | python manage.py shell

REM Собираем статические файлы
echo.
echo ========================================
echo    Сбор статических файлов...
echo ========================================
python manage.py collectstatic --noinput

REM Запускаем сервер
echo.
echo ========================================
echo    Запуск сервера разработки...
echo ========================================
echo.
echo ✓ Сервер запущен!
echo ✓ Откройте браузер и перейдите по адресу:
echo ✓ http://127.0.0.1:8000
echo.
echo ✓ Админ панель:
echo ✓ http://127.0.0.1:8000/admin
echo ✓ Логин: admin
echo ✓ Пароль: admin123
echo.
echo Для остановки сервера нажмите Ctrl+C
echo.
python manage.py runserver 127.0.0.1:8000

pause