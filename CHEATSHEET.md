# 🚀 Шпаргалка Solana DEX Trading Bot

## ⚡ Быстрый старт

```bash
# Автоматическая установка
chmod +x install.sh
./install.sh

# Проверка здоровья
./health_check.sh

# Запуск через Docker
docker-compose up -d
```

## 🎯 Основные команды

### 📊 Управление сервисами
```bash
# Статус всех сервисов
make status

# Запуск локально
make run-local

# Запуск через Docker
make run-docker

# Остановка
make stop

# Перезапуск
make restart
```

### 🧪 Тестирование
```bash
# Все тесты
make test

# Тесты с покрытием
make test-coverage

# Конкретный тест
pytest tests/test_risk_engine.py -v
```

### 🧹 Очистка
```bash
# Очистка логов
make clean-logs

# Полная очистка
make clean-all

# Очистка Docker
make clean-docker
```

## 🌐 Доступ к приложению

| Сервис | URL | Логин/Пароль |
|--------|-----|---------------|
| **Web UI** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Grafana** | http://localhost:3000 | admin/admin |
| **Prometheus** | http://localhost:9090 | - |

## 📱 API Endpoints

### 🔍 Основные endpoints
```bash
# Проверка здоровья
GET /api/health

# Метрики Prometheus
GET /api/metrics

# Котировки Jupiter
GET /api/quotes?in=SOL&out=USDC&amount=1

# Симуляция сделки
POST /api/simulate

# Выполнение сделки
POST /api/trade

# Позиции
GET /api/positions

# P&L отчеты
GET /api/pnl
```

### 🔧 Тестирование API
```bash
# Health check
curl http://localhost:8000/api/health

# Получение котировок
curl "http://localhost:8000/api/quotes?in=SOL&out=USDC&amount=1"

# Симуляция сделки
curl -X POST "http://localhost:8000/api/simulate" \
  -H "Content-Type: application/json" \
  -d '{"token_in":"SOL","token_out":"USDC","amount":"1.0"}'
```

## ⚙️ Конфигурация (.env)

### 🔑 Ключевые настройки
```bash
# Solana
SOLANA_NETWORK=devnet
SOLANA_RPC_URL=https://api.devnet.solana.com
JUPITER_API_URL=https://quote-api.jup.ag/v6

# Торговля
ENABLE_REAL_TRADES=false
PAPER_TRADING=true
MAX_POSITION_SIZE_USD=1000
MAX_DAILY_LOSS_USD=100

# База данных
DATABASE_URL=postgresql://trading_bot:password@localhost:5432/trading_bot
REDIS_URL=redis://localhost:6379

# Уведомления
TELEGRAM_BOT_TOKEN=your_token
DISCORD_WEBHOOK_URL=your_webhook

# Мониторинг
LOG_LEVEL=INFO
METRICS_ENABLED=true
```

## 🎯 Стратегии торговли

### 📋 Momentum Scalping
```json
{
  "strategy": "momentum_scalping",
  "min_volume_change": 5.0,
  "max_hold_time": 30,
  "stop_loss": 3.0,
  "take_profit": 5.0
}
```

### 📋 Mean Reversion
```json
{
  "strategy": "mean_reversion",
  "bollinger_period": 20,
  "deviation_multiplier": 2.0,
  "rsi_oversold": 30,
  "rsi_overbought": 70
}
```

### 📋 Arbitrage
```json
{
  "strategy": "arbitrage",
  "min_spread": 0.5,
  "max_slippage": 0.1,
  "gas_optimization": true
}
```

## 🔒 Risk Engine параметры

### ⚠️ Проверки безопасности
```bash
# Минимальная ликвидность
MIN_TVL_USD=10000

# Максимальное проскальзывание
MAX_SLIPPAGE_PERCENT=5.0

# Минимальная глубина пула
MIN_POOL_DEPTH_USD=5000

# Максимальные налоги
MAX_TAX_PERCENT=10.0

# Проверка honeypot
HONEYPOT_CHECK_ENABLED=true

# Проверка rugpull
RUGPULL_CHECK_ENABLED=true
```

### 🚨 Пороги алертов
```bash
# Высокий риск
HIGH_RISK_THRESHOLD=0.8

# Средний риск
MEDIUM_RISK_THRESHOLD=0.5

# Низкий риск
LOW_RISK_THRESHOLD=0.2
```

## 🎯 Снайпер-бот настройки

### ⚙️ Параметры мониторинга
```bash
# Автоматическая торговля
AUTO_TRADING_ENABLED=true

# Минимальная ликвидность
MIN_LIQUIDITY_USD=5000

# Максимальное проскальзывание
MAX_SNIPER_SLIPPAGE=3.0

# Быстрый выход
QUICK_EXIT_ENABLED=true
QUICK_EXIT_TP_PERCENT=10.0
QUICK_EXIT_SL_PERCENT=5.0
```

### 🔍 Фильтры токенов
```bash
# Минимальный возраст токена (минуты)
MIN_TOKEN_AGE_MINUTES=5

# Минимальный объем торгов
MIN_TRADING_VOLUME_USD=1000

# Максимальная рыночная капитализация
MAX_MARKET_CAP_USD=1000000

# Исключенные токены
EXCLUDED_TOKENS=SCAM,RUG,FAKE
```

## 📊 Мониторинг и метрики

### 📈 Prometheus метрики
```bash
# Торговые метрики
trades_total{status,strategy}
trade_pnl_total{strategy}
risk_blocked_total{reason}

# Системные метрики
portfolio_value_usd
rpc_latency_ms
sniper_trades_total{status}

# HTTP метрики
http_requests_total{method,endpoint,status}
http_request_duration_seconds{method,endpoint}
```

### 📊 Grafana дашборды
- **Trading Bot Overview** - общий обзор
- **Risk Engine Metrics** - метрики risk engine
- **Portfolio Performance** - производительность портфеля
- **System Health** - здоровье системы

## 🔔 Уведомления

### 📱 Telegram
```bash
# Создание бота
1. Напишите @BotFather
2. /newbot
3. Укажите имя и username
4. Получите токен

# Настройка в .env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=your_chat_id
```

### 🎮 Discord
```bash
# Создание webhook
1. Настройки сервера → Интеграции
2. Webhooks → Новый webhook
3. Скопируйте URL

# Настройка в .env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### 📧 Email
```bash
# SMTP настройки
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_TO=notifications@example.com
```

## 🚨 Устранение неполадок

### 🔍 Диагностика
```bash
# Проверка процессов
ps aux | grep python

# Проверка портов
netstat -tulpn | grep -E ':(8000|5432|6379)'

# Проверка логов
tail -f logs/app.log
tail -f logs/worker.log
tail -f logs/sniper.log
```

### 🛠 Перезапуск сервисов
```bash
# Через systemd (Linux)
sudo systemctl restart solana-trading-bot
sudo systemctl restart solana-trading-worker
sudo systemctl restart solana-trading-sniper

# Через процессы
pkill -f "python run.py"
pkill -f "python run_worker.py"
pkill -f "python run_sniper.py"
```

### 🔧 Проверка БД
```bash
# Подключение к PostgreSQL
psql -U trading_bot -d trading_bot -h localhost

# Проверка таблиц
\dt

# Проверка данных
SELECT COUNT(*) FROM trades;
SELECT COUNT(*) FROM positions;
```

## 📚 Полезные команды

### 🐍 Python окружение
```bash
# Активация
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Обновление
pip install --upgrade -r requirements.txt

# Проверка установленных пакетов
pip list
```

### 🐳 Docker
```bash
# Сборка образов
docker-compose build

# Запуск в фоне
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down

# Очистка
docker-compose down -v --remove-orphans
```

### 🗄️ База данных
```bash
# Применение миграций
alembic upgrade head

# Создание новой миграции
alembic revision --autogenerate -m "description"

# Откат миграции
alembic downgrade -1

# Сброс БД
alembic downgrade base
```

## 💡 Советы по использованию

### 🎯 Торговля
1. **Начните с Paper Trading** для тестирования
2. **Используйте небольшие суммы** в начале
3. **Устанавливайте stop-loss** для каждой позиции
4. **Мониторьте risk metrics** регулярно
5. **Диверсифицируйте стратегии**

### 🔒 Безопасность
1. **Никогда не делитесь приватными ключами**
2. **Используйте отдельный кошелек** для торговли
3. **Включите 2FA** для дополнительной защиты
4. **Регулярно обновляйте** зависимости
5. **Мониторьте активность** аккаунта

### 📊 Аналитика
1. **Ведите торговый журнал** всех сделок
2. **Анализируйте ошибки** и учитесь на них
3. **Оптимизируйте параметры** стратегий
4. **Тестируйте новые подходы** на малых суммах
5. **Следите за рыночными трендами**

---

**🎯 Готово! Теперь у вас есть все необходимые команды и настройки!**

Для подробной информации обратитесь к `USER_GUIDE.md` и `INSTALL.md`.