# 🚀 Пошаговый запуск Solana DEX Trading Bot

## 📋 Чек-лист перед запуском

- [ ] Python 3.9+ установлен
- [ ] Git установлен
- [ ] Порты 8000, 5432, 6379 свободны
- [ ] Права sudo (для Linux)
- [ ] 2GB+ свободного места на диске

## 🎯 Способ 1: Автоматическая установка (рекомендуется)

### Шаг 1: Клонирование проекта
```bash
git clone <your-repo-url>
cd solana-dex-trading-bot
```

### Шаг 2: Запуск автоматического установщика
```bash
chmod +x install.sh
./install.sh
```

**Что делает скрипт:**
- ✅ Проверяет систему
- ✅ Устанавливает PostgreSQL, Redis
- ✅ Создает виртуальное окружение Python
- ✅ Устанавливает зависимости
- ✅ Настраивает базу данных
- ✅ Создает systemd сервисы (Linux)
- ✅ Запускает все компоненты

### Шаг 3: Проверка запуска
```bash
# Проверка здоровья системы
./health_check.sh

# Или вручную
curl http://localhost:8000/api/health
```

## 🐳 Способ 2: Docker Compose

### Шаг 1: Проверка Docker
```bash
docker --version
docker-compose --version
```

### Шаг 2: Запуск
```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

## 🛠 Способ 3: Ручная установка

### Шаг 1: Системные зависимости

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib redis-server \
    build-essential python3-dev libpq-dev python3-venv curl
```

#### CentOS/RHEL
```bash
sudo yum install -y postgresql postgresql-server redis \
    gcc python3-devel postgresql-devel python3-pip
```

#### macOS
```bash
brew install postgresql redis
```

### Шаг 2: Настройка PostgreSQL
```bash
# Запуск сервиса
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Создание пользователя и БД
sudo -u postgres createuser --interactive --pwprompt trading_bot
sudo -u postgres createdb trading_bot
```

### Шаг 3: Настройка Redis
```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Проверка
redis-cli ping
```

### Шаг 4: Python окружение
```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Установка зависимостей
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Шаг 5: Конфигурация
```bash
# Копирование конфигурации
cp .env.example .env

# Редактирование настроек
nano .env
```

**Ключевые настройки:**
```bash
# Solana
SOLANA_NETWORK=devnet
SOLANA_RPC_URL=https://api.devnet.solana.com

# Торговля
ENABLE_REAL_TRADES=false
PAPER_TRADING=true

# База данных
DATABASE_URL=postgresql://trading_bot:password@localhost:5432/trading_bot
REDIS_URL=redis://localhost:6379
```

### Шаг 6: Инициализация БД
```bash
# Применение миграций
alembic upgrade head

# Или SQL скрипт
psql -U trading_bot -d trading_bot -f db/init.sql
```

### Шаг 7: Запуск компонентов

#### Терминал 1: FastAPI
```bash
source venv/bin/activate
python run.py
```

#### Терминал 2: Celery Worker
```bash
source venv/bin/activate
python run_worker.py
```

#### Терминал 3: Sniper Bot
```bash
source venv/bin/activate
python run_sniper.py
```

## 🔍 Проверка работоспособности

### 1. Проверка процессов
```bash
# Проверка запущенных процессов
ps aux | grep python

# Проверка портов
netstat -tulpn | grep -E ':(8000|5432|6379)'
```

### 2. Проверка API
```bash
# Health check
curl http://localhost:8000/api/health

# Метрики
curl http://localhost:8000/api/metrics

# Котировки
curl "http://localhost:8000/api/quotes?in=SOL&out=USDC&amount=1"
```

### 3. Проверка логов
```bash
# Логи приложения
tail -f logs/app.log

# Логи worker
tail -f logs/worker.log

# Логи sniper
tail -f logs/sniper.log
```

## 🌐 Доступ к приложению

После успешного запуска:

- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## 📊 Первоначальная настройка

### 1. Создание профиля
- Откройте http://localhost:8000
- Нажмите "Create Profile"
- Введите адрес Solana кошелька
- Настройте параметры торговли

### 2. Настройка стратегий
- Перейдите в раздел "Strategies"
- Включите нужные стратегии
- Настройте параметры risk management

### 3. Настройка уведомлений
- В разделе "Settings" → "Alerts"
- Добавьте Telegram/Discord токены
- Настройте фильтры уведомлений

## 🚨 Устранение неполадок

### Проблема: FastAPI не запускается
```bash
# Проверка логов
tail -f logs/app.log

# Проверка порта
sudo lsof -i :8000

# Перезапуск
pkill -f "python run.py"
python run.py
```

### Проблема: Ошибка подключения к БД
```bash
# Проверка статуса PostgreSQL
sudo systemctl status postgresql

# Проверка подключения
psql -U trading_bot -d trading_bot -h localhost

# Перезапуск
sudo systemctl restart postgresql
```

### Проблема: Redis не отвечает
```bash
# Проверка статуса
sudo systemctl status redis-server

# Проверка подключения
redis-cli ping

# Перезапуск
sudo systemctl restart redis-server
```

### Проблема: Зависимости не установлены
```bash
# Активация виртуального окружения
source venv/bin/activate

# Переустановка
pip install --force-reinstall -r requirements.txt
```

## 🔄 Управление сервисами

### Через systemd (Linux)
```bash
# Статус
sudo systemctl status solana-trading-bot
sudo systemctl status solana-trading-worker
sudo systemctl status solana-trading-sniper

# Перезапуск
sudo systemctl restart solana-trading-bot

# Остановка
sudo systemctl stop solana-trading-bot
```

### Через процессы
```bash
# Остановка всех компонентов
pkill -f "python run.py"
pkill -f "python run_worker.py"
pkill -f "python run_sniper.py"

# Проверка остановки
ps aux | grep python
```

## 📈 Мониторинг

### Prometheus метрики
- `trades_total` - общее количество сделок
- `trade_pnl_total` - общий P&L
- `risk_blocked_total` - заблокированные сделки
- `portfolio_value_usd` - стоимость портфеля

### Grafana дашборды
- Trading Bot Overview
- Risk Engine Metrics
- Portfolio Performance
- System Health

## 🔒 Безопасность

### Важные настройки
1. **Никогда не храните приватные ключи в коде**
2. **Используйте переменные окружения для секретов**
3. **Включите firewall для продакшена**
4. **Регулярно обновляйте зависимости**

### Продакшен настройки
```bash
# В .env для продакшена
ENVIRONMENT=production
ENABLE_REAL_TRADES=true
PAPER_TRADING=false
LOG_LEVEL=INFO
SECRET_KEY=your_very_secure_secret_key
```

## 🆘 Получение помощи

### Полезные команды
```bash
# Статус всех сервисов
make status

# Перезапуск сервисов
make restart

# Очистка логов
make clean-logs

# Полная очистка
make clean-all
```

### Дополнительная документация
- **README.md** - Обзор проекта
- **QUICKSTART.md** - Быстрый старт
- **INSTALL.md** - Подробная установка
- **/docs** - API документация

---

**🎯 Готово! Ваш Solana DEX Trading Bot запущен и готов к работе!**

Если у вас возникли проблемы, запустите `./health_check.sh` для диагностики или обратитесь к документации.