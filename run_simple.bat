@echo off
echo BG Опросник - Простой запуск
echo.

REM Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден!
    echo Установите Python с https://python.org
    pause
    exit /b 1
)

REM Создаем виртуальное окружение
if not exist "venv" (
    echo Создание виртуального окружения...
    python -m venv venv
)

REM Активируем
echo Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Устанавливаем зависимости
echo Установка зависимостей...
pip install -r requirements.txt

REM Создаем папки
if not exist "staticfiles" mkdir staticfiles
if not exist "media" mkdir media

REM Миграции
echo Создание миграций...
python manage.py makemigrations users
python manage.py makemigrations surveys

echo Применение миграций...
python manage.py migrate

REM Администратор
echo Создание администратора...
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None; user = User.objects.get(username='admin'); user.role = 'admin'; user.can_create_surveys = True; user.save()"

REM Статические файлы
echo Сбор статических файлов...
python manage.py collectstatic --noinput

REM Запуск сервера
echo.
echo Сервер запускается...
echo Сайт: http://127.0.0.1:8000
echo Админка: http://127.0.0.1:8000/admin
echo Логин: admin
echo Пароль: admin123
echo.
echo Для остановки нажмите Ctrl+C
echo.

python manage.py runserver 127.0.0.1:8000

pause