#!/bin/bash

# 🔍 Скрипт проверки здоровья Solana DEX Trading Bot

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    local status=$1
    local message=$2
    
    if [ "$status" = "OK" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    else
        echo -e "${RED}❌ $message${NC}"
    fi
}

echo -e "${BLUE}🔍 Проверка здоровья Solana DEX Trading Bot${NC}"
echo "=================================================="

# Проверка процессов
echo -e "\n${BLUE}📊 Процессы:${NC}"

# FastAPI
if pgrep -f "python run.py" > /dev/null; then
    print_status "OK" "FastAPI приложение запущено"
else
    print_status "ERROR" "FastAPI приложение не запущено"
fi

# Celery Worker
if pgrep -f "python run_worker.py" > /dev/null; then
    print_status "OK" "Celery Worker запущен"
else
    print_status "ERROR" "Celery Worker не запущен"
fi

# Sniper Bot
if pgrep -f "python run_sniper.py" > /dev/null; then
    print_status "OK" "Sniper Bot запущен"
else
    print_status "ERROR" "Sniper Bot не запущен"
fi

# Проверка портов
echo -e "\n${BLUE}🌐 Порты:${NC}"

# FastAPI (8000)
if netstat -tuln 2>/dev/null | grep -q ":8000 "; then
    print_status "OK" "Порт 8000 (FastAPI) открыт"
else
    print_status "ERROR" "Порт 8000 (FastAPI) не открыт"
fi

# PostgreSQL (5432)
if netstat -tuln 2>/dev/null | grep -q ":5432 "; then
    print_status "OK" "Порт 5432 (PostgreSQL) открыт"
else
    print_status "ERROR" "Порт 5432 (PostgreSQL) не открыт"
fi

# Redis (6379)
if netstat -tuln 2>/dev/null | grep -q ":6379 "; then
    print_status "OK" "Порт 6379 (Redis) открыт"
else
    print_status "ERROR" "Порт 6379 (Redis) не открыт"
fi

# Проверка API
echo -e "\n${BLUE}🔌 API:${NC}"

# Health check
if command -v curl > /dev/null; then
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        print_status "OK" "API Health Check доступен"
    else
        print_status "ERROR" "API Health Check недоступен"
    fi
    
    # Metrics
    if curl -s http://localhost:8000/api/metrics > /dev/null 2>&1; then
        print_status "OK" "Prometheus метрики доступны"
    else
        print_status "ERROR" "Prometheus метрики недоступны"
    fi
else
    print_status "WARN" "curl не найден, пропускаем проверку API"
fi

# Проверка сервисов
echo -e "\n${BLUE}🖥️  Системные сервисы:${NC}"

# PostgreSQL
if command -v systemctl > /dev/null; then
    if systemctl is-active --quiet postgresql; then
        print_status "OK" "PostgreSQL активен"
    else
        print_status "ERROR" "PostgreSQL неактивен"
    fi
else
    print_status "WARN" "systemctl не найден, пропускаем проверку сервисов"
fi

# Redis
if command -v systemctl > /dev/null; then
    if systemctl is-active --quiet redis-server; then
        print_status "OK" "Redis активен"
    else
        print_status "ERROR" "Redis неактивен"
    fi
fi

# Проверка файлов
echo -e "\n${BLUE}📁 Файлы:${NC}"

# .env
if [ -f ".env" ]; then
    print_status "OK" "Файл .env существует"
else
    print_status "ERROR" "Файл .env не найден"
fi

# Логи
if [ -d "logs" ]; then
    print_status "OK" "Папка logs существует"
    
    # Проверка логов
    if [ -f "logs/app.log" ]; then
        print_status "OK" "Лог приложения существует"
    fi
    
    if [ -f "logs/worker.log" ]; then
        print_status "OK" "Лог worker существует"
    fi
    
    if [ -f "logs/sniper.log" ]; then
        print_status "OK" "Лог sniper существует"
    fi
else
    print_status "ERROR" "Папка logs не найдена"
fi

# Проверка виртуального окружения
echo -e "\n${BLUE}🐍 Python окружение:${NC}"

if [ -d "venv" ]; then
    print_status "OK" "Виртуальное окружение существует"
    
    # Проверка активации
    if [ -n "$VIRTUAL_ENV" ]; then
        print_status "OK" "Виртуальное окружение активировано"
    else
        print_status "WARN" "Виртуальное окружение не активировано"
    fi
else
    print_status "ERROR" "Виртуальное окружение не найдено"
fi

# Проверка зависимостей
if [ -f "requirements.txt" ]; then
    if [ -n "$VIRTUAL_ENV" ]; then
        # Проверка установленных пакетов
        if python -c "import fastapi" 2>/dev/null; then
            print_status "OK" "FastAPI установлен"
        else
            print_status "ERROR" "FastAPI не установлен"
        fi
        
        if python -c "import sqlalchemy" 2>/dev/null; then
            print_status "OK" "SQLAlchemy установлен"
        else
            print_status "ERROR" "SQLAlchemy не установлен"
        fi
        
        if python -c "import celery" 2>/dev/null; then
            print_status "OK" "Celery установлен"
        else
            print_status "ERROR" "Celery не установлен"
        fi
    else
        print_status "WARN" "Активируйте виртуальное окружение для проверки зависимостей"
    fi
fi

# Итоговая оценка
echo -e "\n${BLUE}📊 Итоговая оценка:${NC}"

# Подсчет статусов
total_checks=0
ok_checks=0
warn_checks=0
error_checks=0

# Простая оценка на основе проверок выше
if pgrep -f "python run.py" > /dev/null; then ((ok_checks++)); else ((error_checks++)); fi
((total_checks++))
if pgrep -f "python run_worker.py" > /dev/null; then ((ok_checks++)); else ((error_checks++)); fi
((total_checks++))
if pgrep -f "python run_sniper.py" > /dev/null; then ((ok_checks++)); else ((error_checks++)); fi
((total_checks++))
if netstat -tuln 2>/dev/null | grep -q ":8000 "; then ((ok_checks++)); else ((error_checks++)); fi
((total_checks++))
if [ -f ".env" ]; then ((ok_checks++)); else ((error_checks++)); fi
((total_checks++))
if [ -d "logs" ]; then ((ok_checks++)); else ((error_checks++)); fi
((total_checks++))

# Расчет процента
if [ $total_checks -gt 0 ]; then
    health_percent=$((ok_checks * 100 / total_checks))
    
    if [ $health_percent -ge 80 ]; then
        echo -e "${GREEN}🎉 Отличное состояние: $health_percent% ($ok_checks/$total_checks)${NC}"
    elif [ $health_percent -ge 60 ]; then
        echo -e "${YELLOW}⚠️  Хорошее состояние: $health_percent% ($ok_checks/$total_checks)${NC}"
    else
        echo -e "${RED}🚨 Критическое состояние: $health_percent% ($ok_checks/$total_checks)${NC}"
    fi
fi

echo -e "\n${BLUE}🔧 Рекомендации:${NC}"
if [ $error_checks -gt 0 ]; then
    echo "• Проверьте логи в папке logs/"
    echo "• Убедитесь что все сервисы запущены"
    echo "• Проверьте настройки в .env файле"
    echo "• Запустите ./install.sh для переустановки"
else
    echo "• Система работает корректно"
    echo "• Откройте http://localhost:8000 для доступа к UI"
    echo "• Проверьте метрики на http://localhost:8000/api/metrics"
fi

echo -e "\n${BLUE}📚 Дополнительная информация:${NC}"
echo "• QUICKSTART.md - Быстрый старт"
echo "• INSTALL.md - Подробная установка"
echo "• README.md - Документация проекта"