#!/bin/bash

# 🚀 Solana DEX Trading Bot - Автоматический установщик
# Автор: AI Assistant
# Версия: 1.0.0

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                Solana DEX Trading Bot                        ║"
    echo "║                    Установщик v1.0.0                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Проверка системы
check_system() {
    print_info "Проверка системы..."
    
    # Проверка OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "ОС: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "ОС: macOS"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        print_success "ОС: Windows"
    else
        print_error "Неподдерживаемая ОС: $OSTYPE"
        exit 1
    fi
    
    # Проверка Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
            print_success "Python: $PYTHON_VERSION"
        else
            print_error "Требуется Python 3.9+, найден: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 не найден"
        exit 1
    fi
    
    # Проверка pip
    if command -v pip3 &> /dev/null; then
        print_success "pip3 найден"
    else
        print_error "pip3 не найден"
        exit 1
    fi
    
    # Проверка Docker (опционально)
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        DOCKER_AVAILABLE=true
        print_success "Docker и Docker Compose найдены"
    else
        DOCKER_AVAILABLE=false
        print_warning "Docker не найден, будет использована локальная установка"
    fi
    
    # Проверка портов
    check_ports
}

# Проверка занятых портов
check_ports() {
    print_info "Проверка портов..."
    
    local ports=(8000 5432 6379 9090 3000)
    local ports_in_use=()
    
    for port in "${ports[@]}"; do
        if command -v netstat &> /dev/null; then
            if netstat -tuln 2>/dev/null | grep -q ":$port "; then
                ports_in_use+=($port)
            fi
        elif command -v ss &> /dev/null; then
            if ss -tuln 2>/dev/null | grep -q ":$port "; then
                ports_in_use+=($port)
            fi
        fi
    done
    
    if [ ${#ports_in_use[@]} -eq 0 ]; then
        print_success "Все необходимые порты свободны"
    else
        print_warning "Занятые порты: ${ports_in_use[*]}"
        print_warning "Возможно потребуется остановить другие сервисы"
    fi
}

# Установка системных зависимостей
install_system_deps() {
    print_info "Установка системных зависимостей..."
    
    if [ "$OS" = "linux" ]; then
        if command -v apt-get &> /dev/null; then
            # Ubuntu/Debian
            print_info "Обновление пакетов..."
            sudo apt-get update
            
            print_info "Установка PostgreSQL, Redis и других зависимостей..."
            sudo apt-get install -y postgresql postgresql-contrib redis-server \
                build-essential python3-dev libpq-dev python3-venv curl
                
        elif command -v yum &> /dev/null; then
            # CentOS/RHEL
            print_info "Установка PostgreSQL, Redis и других зависимостей..."
            sudo yum install -y postgresql postgresql-server redis \
                gcc python3-devel postgresql-devel python3-pip
                
        elif command -v dnf &> /dev/null; then
            # Fedora
            print_info "Установка PostgreSQL, Redis и других зависимостей..."
            sudo dnf install -y postgresql postgresql-server redis \
                gcc python3-devel postgresql-devel python3-pip
        fi
        
    elif [ "$OS" = "macos" ]; then
        if command -v brew &> /dev/null; then
            print_info "Установка PostgreSQL и Redis через Homebrew..."
            brew install postgresql redis
        else
            print_warning "Homebrew не найден. Установите PostgreSQL и Redis вручную"
        fi
    fi
}

# Настройка PostgreSQL
setup_postgresql() {
    print_info "Настройка PostgreSQL..."
    
    if [ "$OS" = "linux" ]; then
        # Запуск PostgreSQL
        if command -v systemctl &> /dev/null; then
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
        fi
        
        # Создание пользователя и БД
        print_info "Создание пользователя базы данных..."
        sudo -u postgres createuser --interactive --pwprompt trading_bot 2>/dev/null || true
        sudo -u postgres createdb trading_bot 2>/dev/null || true
        
    elif [ "$OS" = "macos" ]; then
        if command -v brew &> /dev/null; then
            brew services start postgresql
            # Создание пользователя и БД
            createdb trading_bot 2>/dev/null || true
        fi
    fi
}

# Настройка Redis
setup_redis() {
    print_info "Настройка Redis..."
    
    if [ "$OS" = "linux" ]; then
        if command -v systemctl &> /dev/null; then
            sudo systemctl start redis-server
            sudo systemctl enable redis-server
        fi
    elif [ "$OS" = "macos" ]; then
        if command -v brew &> /dev/null; then
            brew services start redis
        fi
    fi
    
    # Проверка Redis
    if redis-cli ping &> /dev/null; then
        print_success "Redis запущен"
    else
        print_warning "Redis не отвечает, проверьте настройки"
    fi
}

# Создание виртуального окружения
create_venv() {
    print_info "Создание виртуального окружения Python..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Виртуальное окружение создано"
    else
        print_info "Виртуальное окружение уже существует"
    fi
    
    # Активация
    source venv/bin/activate
    
    # Обновление pip
    pip install --upgrade pip setuptools wheel
}

# Установка Python зависимостей
install_python_deps() {
    print_info "Установка Python зависимостей..."
    
    source venv/bin/activate
    
    # Установка основных зависимостей
    pip install -r requirements.txt
    
    # Установка зависимостей для разработки
    pip install -r requirements-dev.txt
    
    print_success "Python зависимости установлены"
}

# Настройка конфигурации
setup_config() {
    print_info "Настройка конфигурации..."
    
    # Создание .env файла
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Файл .env создан из .env.example"
        else
            print_warning "Файл .env.example не найден, создайте .env вручную"
        fi
    else
        print_info "Файл .env уже существует"
    fi
    
    # Создание папки для логов
    mkdir -p logs
    print_success "Папка для логов создана"
}

# Инициализация базы данных
init_database() {
    print_info "Инициализация базы данных..."
    
    source venv/bin/activate
    
    # Проверка подключения к БД
    if command -v psql &> /dev/null; then
        if psql -U trading_bot -d trading_bot -c "SELECT 1;" &> /dev/null; then
            print_success "Подключение к БД успешно"
        else
            print_warning "Не удалось подключиться к БД, проверьте настройки"
            return
        fi
    fi
    
    # Применение миграций Alembic
    if [ -f "alembic.ini" ]; then
        print_info "Применение миграций Alembic..."
        alembic upgrade head || print_warning "Ошибка применения миграций"
    fi
    
    # Инициализация БД через SQL скрипт
    if [ -f "db/init.sql" ]; then
        print_info "Выполнение SQL скрипта инициализации..."
        psql -U trading_bot -d trading_bot -f db/init.sql || print_warning "Ошибка выполнения SQL скрипта"
    fi
}

# Создание systemd сервисов (только для Linux)
create_systemd_services() {
    if [ "$OS" = "linux" ] && command -v systemctl &> /dev/null; then
        print_info "Создание systemd сервисов..."
        
        # Сервис для FastAPI
        sudo tee /etc/systemd/system/solana-trading-bot.service > /dev/null <<EOF
[Unit]
Description=Solana DEX Trading Bot
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

        # Сервис для Celery worker
        sudo tee /etc/systemd/system/solana-trading-worker.service > /dev/null <<EOF
[Unit]
Description=Solana DEX Trading Bot Worker
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python run_worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

        # Сервис для Sniper Bot
        sudo tee /etc/systemd/system/solana-trading-sniper.service > /dev/null <<EOF
[Unit]
Description=Solana DEX Trading Bot Sniper
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python run_sniper.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

        # Перезагрузка systemd
        sudo systemctl daemon-reload
        
        print_success "Systemd сервисы созданы"
    fi
}

# Запуск сервисов
start_services() {
    print_info "Запуск сервисов..."
    
    if [ "$OS" = "linux" ] && command -v systemctl &> /dev/null; then
        # Запуск через systemd
        sudo systemctl start solana-trading-bot
        sudo systemctl start solana-trading-worker
        sudo systemctl start solana-trading-sniper
        
        # Включение автозапуска
        sudo systemctl enable solana-trading-bot
        sudo systemctl enable solana-trading-worker
        sudo systemctl enable solana-trading-sniper
        
        print_success "Сервисы запущены через systemd"
        
    else
        # Запуск в фоне
        print_info "Запуск сервисов в фоновом режиме..."
        
        source venv/bin/activate
        
        # Запуск FastAPI
        nohup python run.py > logs/app.log 2>&1 &
        echo $! > .pid_app
        
        # Запуск Celery worker
        nohup python run_worker.py > logs/worker.log 2>&1 &
        echo $! > .pid_worker
        
        # Запуск Sniper Bot
        nohup python run_sniper.py > logs/sniper.log 2>&1 &
        echo $! > .pid_sniper
        
        print_success "Сервисы запущены в фоновом режиме"
    fi
}

# Проверка работоспособности
health_check() {
    print_info "Проверка работоспособности..."
    
    # Ожидание запуска
    sleep 5
    
    # Проверка FastAPI
    if curl -s http://localhost:8000/api/health > /dev/null; then
        print_success "FastAPI приложение работает"
    else
        print_warning "FastAPI приложение не отвечает"
    fi
    
    # Проверка Prometheus
    if curl -s http://localhost:8000/api/metrics > /dev/null; then
        print_success "Prometheus метрики доступны"
    else
        print_warning "Prometheus метрики недоступны"
    fi
}

# Создание Makefile команд
create_makefile_commands() {
    print_info "Создание Makefile команд..."
    
    if [ -f "Makefile" ]; then
        print_success "Makefile уже существует"
    else
        print_warning "Makefile не найден, создайте вручную"
    fi
}

# Финальные инструкции
show_final_instructions() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🎉 УСТАНОВКА ЗАВЕРШЕНА! 🎉               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${BLUE}🌐 Доступ к приложению:${NC}"
    echo "   • Web UI: http://localhost:8000"
    echo "   • API Docs: http://localhost:8000/docs"
    echo "   • Health Check: http://localhost:8000/api/health"
    
    echo -e "${BLUE}📊 Мониторинг:${NC}"
    echo "   • Prometheus: http://localhost:9090"
    echo "   • Grafana: http://localhost:3000 (admin/admin)"
    
    echo -e "${BLUE}📁 Логи:${NC}"
    echo "   • Приложение: logs/app.log"
    echo "   • Worker: logs/worker.log"
    echo "   • Sniper: logs/sniper.log"
    
    echo -e "${BLUE}🛠 Управление:${NC}"
    if [ "$OS" = "linux" ] && command -v systemctl &> /dev/null; then
        echo "   • Статус: sudo systemctl status solana-trading-bot"
        echo "   • Остановка: sudo systemctl stop solana-trading-bot"
        echo "   • Перезапуск: sudo systemctl restart solana-trading-bot"
    else
        echo "   • Остановка: pkill -f 'python run.py'"
        echo "   • Просмотр логов: tail -f logs/*.log"
    fi
    
    echo -e "${BLUE}🔧 Следующие шаги:${NC}"
    echo "   1. Откройте http://localhost:8000"
    echo "   2. Создайте профиль торговца"
    echo "   3. Настройте стратегии и risk management"
    echo "   4. Добавьте уведомления в Settings → Alerts"
    
    echo -e "${BLUE}📚 Документация:${NC}"
    echo "   • README.md - обзор проекта"
    echo "   • INSTALL.md - подробный гайд"
    echo "   • /docs - API документация"
    
    echo -e "${YELLOW}⚠️  Важно:${NC}"
    echo "   • Проверьте настройки в .env файле"
    echo "   • Убедитесь что ENABLE_REAL_TRADES=false для тестирования"
    echo "   • Настройте Solana RPC URL для вашей сети"
}

# Главная функция
main() {
    print_header
    
    print_info "Начинаем установку Solana DEX Trading Bot..."
    
    # Проверка системы
    check_system
    
    # Установка системных зависимостей
    install_system_deps
    
    # Настройка PostgreSQL
    setup_postgresql
    
    # Настройка Redis
    setup_redis
    
    # Создание виртуального окружения
    create_venv
    
    # Установка Python зависимостей
    install_python_deps
    
    # Настройка конфигурации
    setup_config
    
    # Инициализация базы данных
    init_database
    
    # Создание systemd сервисов
    create_systemd_services
    
    # Запуск сервисов
    start_services
    
    # Проверка работоспособности
    health_check
    
    # Создание Makefile команд
    create_makefile_commands
    
    # Финальные инструкции
    show_final_instructions
}

# Обработка аргументов командной строки
case "${1:-}" in
    --help|-h)
        echo "Использование: $0 [опции]"
        echo "Опции:"
        echo "  --help, -h     Показать эту справку"
        echo "  --check-only   Только проверить систему"
        echo "  --no-services  Не запускать сервисы"
        exit 0
        ;;
    --check-only)
        print_header
        check_system
        print_success "Проверка системы завершена"
        exit 0
        ;;
    --no-services)
        print_header
        check_system
        install_system_deps
        setup_postgresql
        setup_redis
        create_venv
        install_python_deps
        setup_config
        init_database
        create_systemd_services
        print_success "Установка завершена без запуска сервисов"
        exit 0
        ;;
    "")
        # Запуск полной установки
        main
        ;;
    *)
        print_error "Неизвестная опция: $1"
        echo "Используйте --help для справки"
        exit 1
        ;;
esac