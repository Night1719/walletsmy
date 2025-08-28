#!/bin/bash

# BG Survey Platform - Скрипт запуска для Linux/Mac
# Автоматическая установка и запуск

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Заголовок
echo
echo "========================================"
echo "    BG Survey Platform v1.0.0"
echo "    BunterGroup"
echo "========================================"
echo

# Проверка Python
print_info "Проверка Python..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        print_error "Python не установлен"
        print_info "Установите Python 3.8+ с https://python.org"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

print_success "Python найден"
$PYTHON_CMD --version

# Проверка pip
print_info "Проверка pip..."
if ! command -v pip3 &> /dev/null; then
    if ! command -v pip &> /dev/null; then
        print_error "pip не установлен"
        print_info "Установите pip для управления пакетами Python"
        exit 1
    else
        PIP_CMD="pip"
    fi
else
    PIP_CMD="pip3"
fi

print_success "pip найден"

# Проверка виртуального окружения
print_info "Проверка виртуального окружения..."
if [ ! -d "venv" ]; then
    print_info "Создание виртуального окружения..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Не удалось создать виртуальное окружение"
        exit 1
    fi
    print_success "Виртуальное окружение создано"
else
    print_info "Виртуальное окружение уже существует"
fi

# Активация виртуального окружения
print_info "Активация виртуального окружения..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Не удалось активировать виртуальное окружение"
    exit 1
fi

# Обновление pip
print_info "Обновление pip..."
$PIP_CMD install --upgrade pip

# Проверка зависимостей
print_info "Проверка зависимостей..."
if ! $PIP_CMD show flask &> /dev/null; then
    print_info "Установка зависимостей..."
    $PIP_CMD install -r requirements.txt
    if [ $? -ne 0 ]; then
        print_error "Не удалось установить зависимости"
        exit 1
    fi
    print_success "Зависимости установлены"
else
    print_info "Зависимости уже установлены"
fi

# Проверка базы данных
print_info "Проверка базы данных..."
if [ ! -f "surveys.db" ]; then
    print_info "База данных не найдена, будет создана автоматически"
fi

# Создание директорий
print_info "Создание необходимых директорий..."
mkdir -p logs uploads static/images

# Проверка прав на запись
if [ ! -w "logs" ] || [ ! -w "uploads" ]; then
    print_warning "Нет прав на запись в директории logs или uploads"
    print_info "Попытка исправления прав..."
    chmod 755 logs uploads 2>/dev/null || true
fi

# Запуск приложения
echo
print_info "Запуск BG Survey Platform..."
print_info "Приложение будет доступно по адресу: http://localhost:5000"
print_info "Для остановки нажмите Ctrl+C"
echo

# Проверка переменных окружения
if [ ! -f ".env" ]; then
    print_warning "Файл .env не найден, создается с настройками по умолчанию"
    cat > .env << EOF
FLASK_CONFIG=development
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///surveys.db
EOF
    print_success "Файл .env создан"
fi

# Запуск приложения
$PYTHON_CMD app.py

echo
print_info "Приложение остановлено"