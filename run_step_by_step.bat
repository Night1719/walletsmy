@echo off
echo ========================================
echo    BG Опросник - Пошаговый запуск
echo ========================================
echo.

echo Шаг 1: Проверка Python...
python --version
if errorlevel 1 (
    echo ❌ Python не найден!
    pause
    exit /b 1
)
echo ✅ Python найден
echo.

echo Шаг 2: Проверка папки...
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
echo.

echo Шаг 3: Создание виртуального окружения...
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
echo.

echo Шаг 4: Активация виртуального окружения...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Ошибка активации виртуального окружения
    pause
    exit /b 1
)
echo ✅ Виртуальное окружение активировано
echo.

echo Шаг 5: Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Ошибка установки зависимостей
    pause
    exit /b 1
)
echo ✅ Зависимости установлены
echo.

echo Шаг 6: Создание папок...
if not exist "staticfiles" mkdir staticfiles
if not exist "media" mkdir media
echo ✅ Папки созданы
echo.

echo Шаг 7: Миграции...
python manage.py makemigrations users
python manage.py makemigrations surveys
python manage.py migrate
echo ✅ Миграции применены
echo.

echo Шаг 8: Создание администратора...
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None; user = User.objects.get(username='admin'); user.role = 'admin'; user.can_create_surveys = True; user.save()"
echo ✅ Администратор создан
echo.

echo Шаг 9: Сбор статических файлов...
python manage.py collectstatic --noinput
echo ✅ Статические файлы собраны
echo.

echo ========================================
echo    ВСЕ ГОТОВО! Запускаем сервер...
echo ========================================
echo.
echo 🌐 Сайт: http://127.0.0.1:8000
echo ⚙️ Админка: http://127.0.0.1:8000/admin
echo 👤 Логин: admin
echo 🔒 Пароль: admin123
echo.
echo Для остановки нажмите Ctrl+C
echo.

python manage.py runserver 127.0.0.1:8000

pause