# 💡 Примеры использования Solana DEX Trading Bot

## 🚀 Сценарии использования

### 📊 Сценарий 1: Начинающий трейдер

#### Цель
Научиться торговать на Solana DEX с минимальными рисками

#### Настройки
```bash
# .env файл
ENABLE_REAL_TRADES=false          # Только paper trading
PAPER_TRADING=true
MAX_POSITION_SIZE_USD=100         # Небольшие позиции
MAX_DAILY_LOSS_USD=50             # Ограничение убытков
RISK_TOLERANCE=low                 # Низкий риск
```

#### Стратегия
1. **Mean Reversion** - торговля на возврате к среднему
2. **Параметры**:
   - Bollinger Bands Period: 20
   - RSI Oversold: 25
   - RSI Overbought: 75
   - Stop Loss: 2%
   - Take Profit: 4%

#### Пошаговый план
1. Создайте профиль с низким уровнем риска
2. Включите Mean Reversion стратегию
3. Начните с симуляции сделок
4. Анализируйте результаты в Analytics
5. Постепенно увеличивайте размеры позиций

### 📈 Сценарий 2: Опытный трейдер

#### Цель
Максимизировать прибыль с управляемым риском

#### Настройки
```bash
# .env файл
ENABLE_REAL_TRADES=true           # Реальная торговля
PAPER_TRADING=false
MAX_POSITION_SIZE_USD=1000        # Крупные позиции
MAX_DAILY_LOSS_USD=200            # Дневной лимит
RISK_TOLERANCE=medium              # Средний риск
```

#### Стратегии
1. **Momentum Scalping** - быстрая торговля на импульсе
2. **Arbitrage** - арбитраж между DEX
3. **Custom Strategy** - собственная стратегия

#### Параметры Momentum Scalping
```json
{
  "strategy": "momentum_scalping",
  "min_volume_change": 8.0,
  "max_hold_time": 15,
  "stop_loss": 2.5,
  "take_profit": 6.0,
  "volume_threshold": 100000
}
```

#### Параметры Arbitrage
```json
{
  "strategy": "arbitrage",
  "min_spread": 0.8,
  "max_slippage": 0.05,
  "gas_optimization": true,
  "max_execution_time": 30
}
```

### 🎯 Сценарий 3: Снайпер-бот для новых токенов

#### Цель
Автоматическое обнаружение и торговля новыми перспективными токенами

#### Настройки
```bash
# .env файл
AUTO_TRADING_ENABLED=true         # Автоматическая торговля
MIN_LIQUIDITY_USD=10000           # Минимальная ликвидность
MAX_SNIPER_SLIPPAGE=2.0           # Максимальное проскальзывание
QUICK_EXIT_ENABLED=true           # Быстрый выход
QUICK_EXIT_TP_PERCENT=15.0        # Take profit 15%
QUICK_EXIT_SL_PERCENT=7.0         # Stop loss 7%
```

#### Фильтры токенов
```bash
MIN_TOKEN_AGE_MINUTES=3           # Минимальный возраст
MIN_TRADING_VOLUME_USD=5000       # Минимальный объем
MAX_MARKET_CAP_USD=500000         # Максимальная капитализация
EXCLUDED_TOKENS=SCAM,RUG,FAKE     # Исключенные токены
```

#### Risk Engine настройки
```bash
HONEYPOT_CHECK_ENABLED=true       # Проверка honeypot
RUGPULL_CHECK_ENABLED=true        # Проверка rugpull
MIN_TVL_USD=5000                  # Минимальный TVL
MAX_TAX_PERCENT=8.0               # Максимальные налоги
```

## 🔧 Практические примеры

### 📱 Создание сделки через API

#### Пример 1: Простая покупка SOL за USDC
```bash
curl -X POST "http://localhost:8000/api/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "token_in": "USDC",
    "token_out": "SOL",
    "amount": "100.0",
    "strategy": "mean_reversion",
    "risk_level": "low"
  }'
```

#### Пример 2: Продажа токена с проверкой рисков
```bash
curl -X POST "http://localhost:8000/api/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "token_in": "BONK",
    "token_out": "USDC",
    "amount": "1000000.0",
    "strategy": "momentum_scalping",
    "risk_level": "medium"
  }'
```

#### Пример 3: Выполнение реальной сделки
```bash
curl -X POST "http://localhost:8000/api/trade" \
  -H "Content-Type: application/json" \
  -d '{
    "token_in": "USDC",
    "token_out": "SOL",
    "amount": "50.0",
    "strategy": "arbitrage",
    "risk_level": "low",
    "confirm_trade": true
  }'
```

### 📊 Получение аналитики

#### Пример 1: P&L отчет за неделю
```bash
curl "http://localhost:8000/api/pnl?period=weekly&strategy=all"
```

#### Пример 2: P&L по конкретной стратегии
```bash
curl "http://localhost:8000/api/pnl?period=daily&strategy=momentum_scalping"
```

#### Пример 3: График P&L
```bash
curl "http://localhost:8000/api/pnl/chart?period=monthly&format=json"
```

### 🔍 Проверка здоровья системы

#### Пример 1: Health check
```bash
curl http://localhost:8000/api/health
```

#### Пример 2: Prometheus метрики
```bash
curl http://localhost:8000/api/metrics
```

#### Пример 3: Проверка конкретных метрик
```bash
# Только торговые метрики
curl "http://localhost:8000/api/metrics" | grep "trades_total"

# Только метрики risk engine
curl "http://localhost:8000/api/metrics" | grep "risk_blocked_total"
```

## 🎯 Настройка уведомлений

### 📱 Telegram уведомления

#### Создание бота
1. Напишите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Укажите имя бота (например, "Trading Bot")
4. Укажите username (например, "my_trading_bot")
5. Получите токен: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

#### Настройка в .env
```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_NOTIFICATIONS_ENABLED=true
```

#### Тестирование уведомлений
```bash
# Отправка тестового уведомления
curl -X POST "http://localhost:8000/api/test-notification" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "telegram",
    "message": "Test notification from Trading Bot"
  }'
```

### 🎮 Discord уведомления

#### Создание webhook
1. Откройте настройки Discord сервера
2. Перейдите в "Интеграции" → "Webhooks"
3. Нажмите "Новый webhook"
4. Укажите имя и канал
5. Скопируйте webhook URL

#### Настройка в .env
```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/abcdefghijklmnop
DISCORD_NOTIFICATIONS_ENABLED=true
```

## 📊 Мониторинг и аналитика

### 📈 Создание Grafana дашборда

#### Дашборд "Trading Performance"
```json
{
  "dashboard": {
    "title": "Trading Performance",
    "panels": [
      {
        "title": "Daily P&L",
        "type": "graph",
        "targets": [
          {
            "expr": "trade_pnl_total{strategy}",
            "legendFormat": "{{strategy}}"
          }
        ]
      },
      {
        "title": "Win Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(trades_total{status=\"success\"}[24h]) / rate(trades_total[24h]) * 100",
            "legendFormat": "Win Rate %"
          }
        ]
      }
    ]
  }
}
```

### 📊 Prometheus запросы

#### Торговые метрики
```promql
# Общее количество сделок за последние 24 часа
trades_total[24h]

# P&L по стратегиям
trade_pnl_total{strategy}

# Заблокированные сделки по причинам
risk_blocked_total{reason}

# Процент успешных сделок
rate(trades_total{status="success"}[1h]) / rate(trades_total[1h]) * 100
```

#### Системные метрики
```promql
# HTTP запросы по эндпоинтам
http_requests_total{endpoint}

# Время ответа API
histogram_quantile(0.95, http_request_duration_seconds{endpoint="/api/trade"})

# Активные HTTP запросы
http_requests_active{endpoint}
```

## 🚨 Устранение неполадок

### 🔍 Диагностика проблем

#### Проблема: Высокое проскальзывание
```bash
# Проверка ликвидности пула
curl "http://localhost:8000/api/quotes?in=SOL&out=USDC&amount=1000"

# Проверка метрик slippage
curl "http://localhost:8000/api/metrics" | grep "slippage"

# Анализ логов
tail -f logs/app.log | grep "slippage"
```

#### Проблема: Сделки блокируются risk engine
```bash
# Проверка метрик risk engine
curl "http://localhost:8000/api/metrics" | grep "risk_blocked"

# Анализ логов risk engine
tail -f logs/app.log | grep "risk_engine"

# Проверка настроек risk engine
grep "RISK" .env
```

#### Проблема: Снайпер-бот не находит токены
```bash
# Проверка статуса снайпер-бота
ps aux | grep "run_sniper.py"

# Проверка логов снайпер-бота
tail -f logs/sniper.log

# Проверка настроек мониторинга
grep "SNIPER" .env
```

### 🛠 Оптимизация производительности

#### Настройка PostgreSQL
```sql
-- Создание индексов для ускорения запросов
CREATE INDEX idx_trades_timestamp ON trades(timestamp);
CREATE INDEX idx_trades_strategy ON trades(strategy);
CREATE INDEX idx_positions_status ON positions(status);

-- Анализ производительности
ANALYZE trades;
ANALYZE positions;
```

#### Настройка Redis
```bash
# Оптимизация Redis
redis-cli CONFIG SET maxmemory-policy allkeys-lru
redis-cli CONFIG SET save "900 1 300 10 60 10000"
```

## 💡 Продвинутые техники

### 🎯 Создание кастомной стратегии

#### Пример: Grid Trading
```python
class GridTradingStrategy:
    def __init__(self, grid_levels=10, grid_spacing=0.02):
        self.grid_levels = grid_levels
        self.grid_spacing = grid_spacing
    
    def calculate_grid_prices(self, current_price):
        prices = []
        for i in range(self.grid_levels):
            price = current_price * (1 + i * self.grid_spacing)
            prices.append(price)
        return prices
    
    def should_buy(self, current_price, grid_prices):
        # Логика покупки на уровнях сетки
        pass
    
    def should_sell(self, current_price, grid_prices):
        # Логика продажи на уровнях сетки
        pass
```

### 🔄 Автоматическое перебалансирование

#### Скрипт перебалансирования
```bash
#!/bin/bash
# Автоматическое перебалансирование портфеля

# Получение текущего баланса
BALANCE=$(curl -s "http://localhost:8000/api/portfolio/balance" | jq '.total_usd')

# Проверка отклонения от целевого распределения
DEVIATION=$(curl -s "http://localhost:8000/api/portfolio/deviation" | jq '.deviation_percent')

if (( $(echo "$DEVIATION > 5" | bc -l) )); then
    echo "Portfolio deviation: $DEVIATION%. Rebalancing..."
    
    # Выполнение перебалансирования
    curl -X POST "http://localhost:8000/api/portfolio/rebalance" \
      -H "Content-Type: application/json" \
      -d '{"target_allocation": "balanced"}'
fi
```

### 📊 Анализ рыночных данных

#### Скрипт анализа рынка
```python
import requests
import pandas as pd

def analyze_market_conditions():
    # Получение данных о волатильности
    volatility_data = requests.get("http://localhost:8000/api/market/volatility").json()
    
    # Анализ корреляций
    correlation_data = requests.get("http://localhost:8000/api/market/correlations").json()
    
    # Определение оптимальной стратегии
    if volatility_data['current'] > volatility_data['average'] * 1.5:
        return "high_volatility_strategy"
    elif correlation_data['market_correlation'] > 0.8:
        return "diversification_strategy"
    else:
        return "normal_strategy"

# Использование
optimal_strategy = analyze_market_conditions()
print(f"Recommended strategy: {optimal_strategy}")
```

---

**🎯 Готово! Теперь у вас есть практические примеры использования всех возможностей торгового бота!**

Используйте эти примеры как основу для создания собственных торговых стратегий и автоматизации.