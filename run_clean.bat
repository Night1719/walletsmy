@echo off
chcp 65001 >nul
echo ========================================
echo    BG Опросник - Чистый запуск
echo ========================================
echo.

REM Проверяем Python
echo [1/9] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo Установите Python с https://python.org
    pause
    exit /b 1
)
echo ✅ Python найден

REM Проверяем наличие manage.py
echo [2/9] Проверка Django проекта...
if not exist "manage.py" (
    echo ❌ Файл manage.py не найден!
    echo Убедитесь, что вы в папке survey_platform
    echo.
    echo Текущая папка:
    cd
    echo.
    echo Содержимое папки:
    dir
    pause
    exit /b 1
)
echo ✅ manage.py найден

REM Создаем виртуальное окружение
echo [3/9] Создание виртуального окружения...
if not exist "venv" (
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Ошибка создания виртуального окружения
        pause
        exit /b 1
    )
    echo ✅ Виртуальное окружение создано
) else (
    echo ✅ Виртуальное окружение уже существует
)

REM Активируем виртуальное окружение
echo [4/9] Активация виртуального окружения...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Ошибка активации виртуального окружения
    pause
    exit /b 1
)
echo ✅ Виртуальное окружение активировано

REM Обновляем pip
echo [5/9] Обновление pip...
python -m pip install --upgrade pip
echo ✅ pip обновлен

REM Устанавливаем зависимости
echo [6/9] Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Ошибка установки зависимостей
    pause
    exit /b 1
)
echo ✅ Зависимости установлены

REM Создаем необходимые директории
echo [7/9] Создание директорий...
if not exist "staticfiles" mkdir staticfiles
if not exist "media" mkdir media
echo ✅ Директории созданы

REM Создаем миграции
echo [8/9] Создание миграций...
python manage.py makemigrations users
python manage.py makemigrations surveys
echo ✅ Миграции созданы

REM Применяем миграции
echo [9/9] Применение миграций...
python manage.py migrate
echo ✅ Миграции применены

REM Создаем суперпользователя
echo.
echo ========================================
echo    Создание администратора...
echo ========================================
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None; user = User.objects.get(username='admin'); user.role = 'admin'; user.can_create_surveys = True; user.save()"
echo ✅ Администратор создан

REM Собираем статические файлы
echo.
echo ========================================
echo    Сбор статических файлов...
echo ========================================
python manage.py collectstatic --noinput
echo ✅ Статические файлы собраны

REM Запускаем сервер
echo.
echo ========================================
echo    Запуск сервера разработки...
echo ========================================
echo.
echo ✅ Сервер запущен!
echo ✅ Откройте браузер и перейдите по адресу:
echo ✅ http://127.0.0.1:8000
echo.
echo ✅ Админ панель:
echo ✅ http://127.0.0.1:8000/admin
echo ✅ Логин: admin
echo ✅ Пароль: admin123
echo.
echo Для остановки сервера нажмите Ctrl+C
echo.

python manage.py runserver 127.0.0.1:8000

pause