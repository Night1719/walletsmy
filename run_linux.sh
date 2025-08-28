#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================"
echo -e "    BG Опросник - Запуск на Linux/Mac"
echo -e "========================================${NC}"
echo

# Функция для вывода сообщений
print_status() {
    echo -e "${BLUE}[$1/$2]${NC} $3"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Проверяем наличие Python
print_status "1" "8" "Проверка Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    print_success "Python3 найден"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    print_success "Python найден"
else
    print_error "Python не найден!"
    echo "Установите Python 3.8+ с помощью:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi

# Проверяем версию Python
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l) -eq 0 ]]; then
    print_warning "Рекомендуется Python 3.8+ (текущая версия: $PYTHON_VERSION)"
fi

# Проверяем наличие pip
print_status "2" "8" "Проверка pip..."
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    print_error "pip не найден!"
    echo "Установите pip:"
    echo "  $PYTHON_CMD -m ensurepip --upgrade"
    exit 1
fi
print_success "pip найден"

# Создаем виртуальное окружение
print_status "3" "8" "Создание виртуального окружения..."
if [ ! -d "venv" ]; then
    if ! $PYTHON_CMD -m venv venv; then
        print_error "Не удалось создать виртуальное окружение!"
        echo "На Ubuntu/Debian установите: sudo apt install python3-venv"
        exit 1
    fi
    print_success "Виртуальное окружение создано"
else
    print_success "Виртуальное окружение уже существует"
fi

# Активируем виртуальное окружение
print_status "4" "8" "Активация виртуального окружения..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Не удалось активировать виртуальное окружение!"
    exit 1
fi
print_success "Виртуальное окружение активировано"

# Обновляем pip
print_status "5" "8" "Обновление pip..."
$PYTHON_CMD -m pip install --upgrade pip
print_success "pip обновлен"

# Устанавливаем зависимости
print_status "6" "8" "Установка зависимостей..."
if ! pip install -r requirements.txt; then
    print_error "Не удалось установить зависимости!"
    exit 1
fi
print_success "Зависимости установлены"

# Создаем необходимые директории
print_status "7" "8" "Создание директорий..."
mkdir -p staticfiles media
print_success "Директории созданы"

# Проверяем наличие manage.py
print_status "8" "8" "Проверка Django проекта..."
if [ ! -f "manage.py" ]; then
    print_error "Файл manage.py не найден!"
    echo "Убедитесь, что вы находитесь в корневой папке проекта"
    exit 1
fi
print_success "manage.py найден"

# Создаем миграции
echo
echo -e "${BLUE}========================================"
echo -e "    Создание миграций базы данных..."
echo -e "========================================${NC}"
$PYTHON_CMD manage.py makemigrations users
$PYTHON_CMD manage.py makemigrations surveys

# Применяем миграции
echo
echo -e "${BLUE}========================================"
echo -e "    Применение миграций..."
echo -e "========================================${NC}"
$PYTHON_CMD manage.py migrate

# Создаем суперпользователя
echo
echo -e "${BLUE}========================================"
echo -e "    Создание администратора..."
echo -e "========================================${NC}"
echo "Создаем суперпользователя admin/admin123..."
$PYTHON_CMD manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    admin.role = 'admin'
    admin.can_create_surveys = True
    admin.save()
    print('Суперпользователь создан: admin/admin123')
else:
    print('Суперпользователь admin уже существует')
    user = User.objects.get(username='admin')
    user.role = 'admin'
    user.can_create_surveys = True
    user.save()
    print('Права администратора обновлены')
"

# Собираем статические файлы
echo
echo -e "${BLUE}========================================"
echo -e "    Сбор статических файлов..."
echo -e "========================================${NC}"
$PYTHON_CMD manage.py collectstatic --noinput

# Запускаем сервер
echo
echo -e "${BLUE}========================================"
echo -e "    Запуск сервера разработки..."
echo -e "========================================${NC}"
echo
echo -e "${GREEN}✓${NC} Сервер запущен!"
echo -e "${GREEN}✓${NC} Откройте браузер и перейдите по адресу:"
echo -e "${GREEN}✓${NC} http://127.0.0.1:8000"
echo
echo -e "${GREEN}✓${NC} Админ панель:"
echo -e "${GREEN}✓${NC} http://127.0.0.1:8000/admin"
echo -e "${GREEN}✓${NC} Логин: admin"
echo -e "${GREEN}✓${NC} Пароль: admin123"
echo
echo "Для остановки сервера нажмите Ctrl+C"
echo

$PYTHON_CMD manage.py runserver 127.0.0.1:8000