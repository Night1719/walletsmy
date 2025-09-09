#!/bin/bash

# Скрипт запуска админского портала

echo "🚀 Запуск Админского Портала..."

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Пожалуйста, установите Docker и попробуйте снова."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Пожалуйста, установите Docker Compose и попробуйте снова."
    exit 1
fi

# Создание необходимых директорий
echo "📁 Создание директорий..."
mkdir -p scripts/monitoring scripts/backup scripts/maintenance
mkdir -p logs/system logs/application logs/errors

# Копирование примеров скриптов
echo "📋 Копирование примеров скриптов..."
cp example_monitoring.py scripts/monitoring/
cp example_backup.py scripts/backup/
cp example_maintenance.py scripts/maintenance/

# Установка прав на выполнение
chmod +x scripts/*/*.py

# Запуск через Docker Compose
echo "🐳 Запуск контейнеров..."
docker-compose up --build -d

# Ожидание запуска сервисов
echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверка статуса
echo "🔍 Проверка статуса сервисов..."
docker-compose ps

echo ""
echo "✅ Админский портал запущен!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Для остановки используйте: docker-compose down"
echo "📋 Для просмотра логов: docker-compose logs -f"