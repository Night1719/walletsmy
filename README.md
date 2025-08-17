# Solana Trading Bot Platform

Платформа для трейдинга на Solana DEX через Jupiter API с интерфейсом в стиле Discord.

## 🚀 Возможности

- **Трейдинг-бот**: Автоматическая торговля через Jupiter API
- **Снайпер-бот**: Мониторинг новых токенов с защитой от скама
- **Risk Engine**: Проверки безопасности перед каждой сделкой
- **Аналитика**: PNL, win-rate, графики портфеля
- **Paper Trading**: Режим симуляции без реальных денег
- **Discord-подобный UI**: Современный интерфейс с темной темой

## 🏗️ Архитектура

```
project/
├── app/           # FastAPI приложение + API + HTML рендеринг
├── bot/           # Ядро трейдера: Jupiter, risk engine, sniper bot
├── worker/        # Celery задачи (market scan, execute trades)
├── db/            # SQLAlchemy модели + Alembic миграции
├── templates/     # Jinja2 HTML (UX как Discord)
├── static/        # CSS/JS (Tailwind, Alpine.js)
└── tests/         # pytest тесты
```

## 🛠️ Технологии

- **Backend**: FastAPI (async, swagger)
- **UI**: Jinja2 + HTMX + Alpine.js
- **CSS**: TailwindCSS (dark theme)
- **Charts**: Chart.js
- **DB**: PostgreSQL + SQLAlchemy + Alembic
- **Worker**: Celery + Redis
- **Метрики**: Prometheus + Grafana
- **Solana**: solana-py, Jupiter API

## 🚀 Быстрый старт

### 1. Клонирование и настройка

```bash
git clone <repository>
cd solana-trading-bot
cp .env.example .env
# Настройте .env файл с вашими ключами
```

### 2. Запуск через Docker

```bash
docker-compose up -d
```

### 3. Доступ к приложению

- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090

## ⚙️ Конфигурация

### Переменные окружения

```bash
# Solana
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_DEVNET_RPC_URL=https://api.devnet.solana.com
JUPITER_API_URL=https://quote-api.jup.ag/v6

# Торговля
ENABLE_REAL_TRADES=false  # Paper trading по умолчанию
WALLET_PRIVATE_KEY=your_private_key
MAX_POSITION_SIZE_USD=1000
MAX_DAILY_LOSS_USD=100

# База данных
DATABASE_URL=postgresql://user:pass@localhost/trading_bot
REDIS_URL=redis://localhost:6379

# Уведомления
TELEGRAM_BOT_TOKEN=your_token
DISCORD_WEBHOOK_URL=your_webhook
```

## 🔒 Risk Engine

### Обязательные проверки

- **Liquidity**: Минимальный TVL и глубина пула
- **Slippage**: Максимально допустимый проскальзывание
- **Fees**: Анализ комиссий vs потенциальной прибыли
- **Honeypot Detection**: Проверка возможности продажи токена
- **Rug Pull Protection**: Анализ mint/freeze authority
- **Position Limits**: Ограничения по размеру позиции
- **Stop-loss/Take-profit**: Автоматическое управление рисками

## 📊 API Endpoints

- `GET /` - Главная страница
- `GET /api/health` - Статус системы
- `GET /api/metrics` - Prometheus метрики
- `GET /api/quotes` - Котировки Jupiter
- `POST /api/simulate` - Симуляция сделки с risk report
- `POST /api/trade` - Исполнение сделки
- `GET /api/positions` - Портфель позиций
- `GET /api/pnl` - История P&L

## 🎯 Стратегии

- **Cross-pool Arbitrage**: Арбитраж между пулами
- **Momentum Scalping**: Скальпинг по моменту
- **Mean Reversion**: Торговля на возврат к среднему

## 📈 Метрики

- Общее количество сделок
- P&L по стратегиям
- Заблокированные сделки (risk engine)
- Стоимость портфеля
- Latency RPC
- Снайпер-сделки

## 🧪 Тестирование

```bash
# Запуск тестов
pytest

# Тесты с coverage
pytest --cov=app --cov=bot

# Тесты risk engine
pytest tests/test_risk_engine.py

# E2E тесты
pytest tests/test_e2e.py
```

## 🔧 Разработка

### Установка зависимостей

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Миграции БД

```bash
alembic upgrade head
alembic revision --autogenerate -m "description"
```

### Локальный запуск

```bash
# Terminal 1: FastAPI
uvicorn app.main:app --reload --port 8000

# Terminal 2: Celery Worker
celery -A worker.celery_app worker --loglevel=info

# Terminal 3: Redis
redis-server

# Terminal 4: PostgreSQL
# Запустите PostgreSQL локально
```

## 📱 UI Особенности

- **Discord-подобный интерфейс** с темной темой
- **Левая панель**: Профили, кошельки, стратегии
- **Центральная область**: Графики, таблицы, симулятор
- **Правая панель**: Активность, сделки, ошибки
- **Каналы**: Dashboard, Markets, Positions, Strategies
- **Анимации**: Плавные переходы через Alpine.js

## 🚨 Безопасность

- Приватные ключи только через .env/KMS
- Paper trading по умолчанию
- ACL роли (admin/trader/viewer)
- Devnet/Mainnet переключатель
- Валидация всех входных данных

## 📊 Мониторинг

- **Prometheus**: Метрики производительности
- **Grafana**: Дашборды и алерты
- **Structured Logs**: Ротация и экспорт в OpenTelemetry
- **Health Checks**: Статус всех компонентов

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Commit изменения
4. Push в branch
5. Создайте Pull Request

## 📄 Лицензия

MIT License - см. файл LICENSE для деталей.

## 🆘 Поддержка

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Wiki**: Документация и примеры

---

**⚠️ Внимание**: Торговля криптовалютами связана с высокими рисками. Используйте только те средства, потерю которых можете себе позволить.