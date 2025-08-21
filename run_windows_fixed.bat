@echo off
echo ========================================
echo    BG Опросник - Бантер Групп
echo ========================================
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден!
    echo Установите Python 3.8+ с https://python.org
    echo.
    pause
    exit /b 1
)

REM Проверяем наличие pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: pip не найден!
    echo Установите pip или переустановите Python
    echo.
    pause
    exit /b 1
)

echo Python найден. Создаем виртуальное окружение...
echo.

REM Создаем виртуальное окружение если его нет
if not exist "venv" (
    echo Создание виртуального окружения...
    python -m venv venv
    if errorlevel 1 (
        echo ОШИБКА: Не удалось создать виртуальное окружение!
        pause
        exit /b 1
    )
)

REM Активируем виртуальное окружение
echo Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Устанавливаем зависимости
echo.
echo Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo ОШИБКА: Не удалось установить зависимости!
    pause
    exit /b 1
)

REM Создаем необходимые директории
echo.
echo Создание директорий...
if not exist "staticfiles" mkdir staticfiles
if not exist "media" mkdir media

REM Создаем миграции
echo.
echo Создание миграций базы данных...
python manage.py makemigrations users
python manage.py makemigrations surveys

REM Применяем миграции
echo.
echo Применение миграций...
python manage.py migrate
if errorlevel 1 (
    echo ОШИБКА: Не удалось применить миграции!
    pause
    exit /b 1
)

REM Создаем суперпользователя если его нет
echo.
echo Проверка суперпользователя...
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Создание суперпользователя...')
    admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    admin.role = 'admin'
    admin.can_create_surveys = True
    admin.save()
    print('Суперпользователь создан:')
    print('Логин: admin')
    print('Пароль: admin123')
else:
    print('Суперпользователь уже существует')
"

REM Собираем статические файлы
echo.
echo Сбор статических файлов...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo ПРЕДУПРЕЖДЕНИЕ: Не удалось собрать статические файлы!
    echo Продолжаем без статических файлов...
)

echo.
echo ========================================
echo    Запуск сервера разработки...
echo ========================================
echo.
echo Сервер будет доступен по адресу: http://127.0.0.1:8000
echo Админ панель: http://127.0.0.1:8000/admin
echo.
echo Для остановки сервера нажмите Ctrl+C
echo.

REM Запускаем сервер
python manage.py runserver

echo.
echo Сервер остановлен.
pause