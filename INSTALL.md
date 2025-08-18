# 🚀 Гайд по установке и запуску Solana DEX Trading Bot

## 📋 Предварительные требования

### Системные требования
- **OS**: Linux (Ubuntu 20.04+), macOS, Windows (WSL2)
- **Python**: 3.9+ 
- **RAM**: минимум 4GB, рекомендуется 8GB+
- **Диск**: минимум 2GB свободного места
- **Docker**: версия 20.10+ (для Docker-установки)

### Проверка системы
```bash
# Проверка Python
python3 --version  # Должен быть 3.9+

# Проверка Docker (если используете)
docker --version
docker-compose --version

# Проверка доступности портов
netstat -tulpn | grep -E ':(8000|5432|6379|9090|3000)'
```

## 🛠 Способ 1: Быстрая установка через скрипт

### Автоматическая установка
```bash
# Скачать и запустить установочный скрипт
chmod +x install.sh
./install.sh
```

Скрипт автоматически:
- Установит все зависимости
- Настроит базу данных
- Создаст конфигурационные файлы
- Запустит все сервисы

## 🔧 Способ 2: Ручная установка

### 1. Клонирование и настройка
```bash
# Клонирование репозитория
git clone <your-repo-url>
cd solana-dex-trading-bot

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt
pip install -r requirements-dev.txt  # для разработки
```

### 2. Настройка окружения
```bash
# Копирование конфигурации
cp .env.example .env

# Редактирование .env файла
nano .env
```

**Важные настройки в .env:**
```bash
# Solana настройки
SOLANA_NETWORK=devnet  # или mainnet
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_DEVNET_RPC_URL=https://api.devnet.solana.com

# Торговые настройки
ENABLE_REAL_TRADES=false  # true только для реальной торговли
PAPER_TRADING=true

# База данных
DATABASE_URL=postgresql://user:password@localhost:5432/trading_bot

# Redis
REDIS_URL=redis://localhost:6379

# Уведомления
TELEGRAM_BOT_TOKEN=your_token
DISCORD_WEBHOOK_URL=your_webhook
```

### 3. Настройка базы данных

#### PostgreSQL установка (Ubuntu/Debian)
```bash
# Установка PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Создание пользователя и БД
sudo -u postgres createuser --interactive trading_bot
sudo -u postgres createdb trading_bot

# Установка пароля
sudo -u postgres psql
ALTER USER trading_bot PASSWORD 'your_password';
\q
```

#### Инициализация БД
```bash
# Применение миграций
alembic upgrade head

# Или инициализация с нуля
psql -U trading_bot -d trading_bot -f db/init.sql
```

### 4. Установка Redis
```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis

# Windows (WSL2)
sudo apt install redis-server
```

## 🚀 Запуск приложения

### Способ 1: Через Makefile (рекомендуется)
```bash
# Установка зависимостей
make install

# Запуск всех сервисов локально
make run-local

# Или через Docker
make run-docker

# Остановка
make stop
```

### Способ 2: Ручной запуск

#### Запуск FastAPI приложения
```bash
# В одном терминале
python run.py
# Приложение будет доступно на http://localhost:8000
```

#### Запуск Celery worker
```bash
# В другом терминале
python run_worker.py
```

#### Запуск снайпер бота
```bash
# В третьем терминале
python run_sniper.py
```

### Способ 3: Docker Compose (полная автоматизация)
```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

## 🌐 Доступ к приложению

После запуска:

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

## 🔍 Проверка работоспособности

### Проверка API
```bash
# Проверка здоровья системы
curl http://localhost:8000/api/health

# Проверка метрик
curl http://localhost:8000/api/metrics

# Получение котировок
curl "http://localhost:8000/api/quotes?in=SOL&out=USDC&amount=1"
```

### Проверка логов
```bash
# Логи FastAPI
tail -f logs/app.log

# Логи Celery
tail -f logs/worker.log

# Логи снайпер бота
tail -f logs/sniper.log
```

## 🧪 Тестирование

### Запуск тестов
```bash
# Все тесты
make test

# Конкретный тест
pytest tests/test_risk_engine.py -v

# С покрытием
make test-coverage
```

### Тестирование торговли
```bash
# Симуляция сделки
curl -X POST "http://localhost:8000/api/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "token_in": "SOL",
    "token_out": "USDC", 
    "amount": "1.0"
  }'
```

## 🚨 Устранение неполадок

### Частые проблемы

#### 1. Ошибка подключения к БД
```bash
# Проверка статуса PostgreSQL
sudo systemctl status postgresql

# Проверка подключения
psql -U trading_bot -d trading_bot -h localhost
```

#### 2. Ошибка Redis
```bash
# Проверка статуса Redis
sudo systemctl status redis-server

# Проверка подключения
redis-cli ping
```

#### 3. Проблемы с Solana RPC
```bash
# Проверка доступности RPC
curl -X POST https://api.devnet.solana.com \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"getHealth"}'
```

#### 4. Проблемы с портами
```bash
# Проверка занятых портов
sudo netstat -tulpn | grep -E ':(8000|5432|6379)'

# Освобождение порта (если занят)
sudo fuser -k 8000/tcp
```

### Логи и отладка
```bash
# Включение debug режима
export LOG_LEVEL=DEBUG

# Запуск с подробными логами
python run.py --log-level debug

# Просмотр системных логов
journalctl -u postgresql -f
journalctl -u redis-server -f
```

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

## 📈 Мониторинг и метрики

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

## 🔄 Обновление

### Обновление кода
```bash
git pull origin main
pip install -r requirements.txt
alembic upgrade head
```

### Обновление Docker образов
```bash
docker-compose pull
docker-compose up -d
```

## 📞 Поддержка

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

### Дополнительная помощь
- Проверьте логи в папке `logs/`
- Изучите документацию API на `/docs`
- Проверьте метрики Prometheus
- Изучите конфигурацию в `.env`

---

**🎯 Готово! Ваш Solana DEX Trading Bot запущен и готов к работе!**