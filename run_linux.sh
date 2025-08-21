#!/bin/bash

echo "========================================"
echo "    BG Опросник - Бантер Групп"
echo "========================================"
echo

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "ОШИБКА: Python3 не найден!"
    echo "Установите Python 3.8+ с помощью:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  macOS: brew install python3"
    echo
    exit 1
fi

# Проверяем наличие pip
if ! command -v pip3 &> /dev/null; then
    echo "ОШИБКА: pip3 не найден!"
    echo "Установите pip3 или переустановите Python3"
    echo
    exit 1
fi

echo "Python3 найден. Создаем виртуальное окружение..."
echo

# Создаем виртуальное окружение если его нет
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ОШИБКА: Не удалось создать виртуальное окружение!"
        exit 1
    fi
fi

# Активируем виртуальное окружение
echo "Активация виртуального окружения..."
source venv/bin/activate

# Обновляем pip
echo "Обновление pip..."
pip install --upgrade pip

# Устанавливаем зависимости
echo
echo "Установка зависимостей..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ОШИБКА: Не удалось установить зависимости!"
    exit 1
fi

# Создаем миграции
echo
echo "Создание миграций базы данных..."
python manage.py makemigrations
if [ $? -ne 0 ]; then
    echo "ОШИБКА: Не удалось создать миграции!"
    exit 1
fi

# Применяем миграции
echo
echo "Применение миграций..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "ОШИБКА: Не удалось применить миграции!"
    exit 1
fi

# Создаем суперпользователя если его нет
echo
echo "Проверка суперпользователя..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Создание суперпользователя...')
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Суперпользователь создан:')
    print('Логин: admin')
    print('Пароль: admin123')
else:
    print('Суперпользователь уже существует')
"

# Собираем статические файлы
echo
echo "Сбор статических файлов..."
python manage.py collectstatic --noinput
if [ $? -ne 0 ]; then
    echo "ПРЕДУПРЕЖДЕНИЕ: Не удалось собрать статические файлы!"
fi

echo
echo "========================================"
echo "    Запуск сервера разработки..."
echo "========================================"
echo
echo "Сервер будет доступен по адресу: http://127.0.0.1:8000"
echo "Админ панель: http://127.0.0.1:8000/admin"
echo
echo "Для остановки сервера нажмите Ctrl+C"
echo

# Запускаем сервер
python manage.py runserver

echo
echo "Сервер остановлен."