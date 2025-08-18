# 🚀 Быстрый старт Solana DEX Trading Bot

## ⚡ Установка за 5 минут

### 1. Автоматическая установка (рекомендуется)
```bash
# Сделать скрипт исполняемым и запустить
chmod +x install.sh
./install.sh
```

### 2. Проверка системы (без установки)
```bash
./install.sh --check-only
```

### 3. Установка без запуска сервисов
```bash
./install.sh --no-services
```

## 🐳 Быстрый запуск через Docker

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

## 🛠 Ручной запуск

### Установка зависимостей
```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Установка пакетов
pip install -r requirements.txt
```

### Настройка
```bash
# Копирование конфигурации
cp .env.example .env

# Редактирование настроек
nano .env
```

### Запуск
```bash
# Терминал 1: FastAPI
python run.py

# Терминал 2: Celery Worker
python run_worker.py

# Терминал 3: Sniper Bot
python run_sniper.py
```

## 🌐 Доступ к приложению

- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## 📋 Первые шаги

1. **Откройте** http://localhost:8000
2. **Создайте профиль** торговца
3. **Настройте стратегии** в разделе Strategies
4. **Добавьте уведомления** в Settings → Alerts
5. **Протестируйте** симуляцию сделки

## 🚨 Если что-то не работает

### Проверка логов
```bash
# Логи приложения
tail -f logs/app.log

# Логи worker
tail -f logs/worker.log

# Логи снайпер бота
tail -f logs/sniper.log
```

### Проверка сервисов
```bash
# Статус PostgreSQL
sudo systemctl status postgresql

# Статус Redis
sudo systemctl status redis-server

# Проверка портов
netstat -tulpn | grep -E ':(8000|5432|6379)'
```

### Перезапуск
```bash
# Через systemd (Linux)
sudo systemctl restart solana-trading-bot

# Или остановить процессы
pkill -f 'python run.py'
pkill -f 'python run_worker.py'
pkill -f 'python run_sniper.py'
```

## 📚 Подробная документация

- **INSTALL.md** - Полный гайд по установке
- **README.md** - Обзор проекта и архитектура
- **/docs** - API документация (после запуска)

## 🆘 Поддержка

### Полезные команды
```bash
# Статус всех сервисов
make status

# Перезапуск
make restart

# Очистка
make clean-all
```

### Проверка здоровья
```bash
# API health check
curl http://localhost:8000/api/health

# Prometheus метрики
curl http://localhost:8000/api/metrics
```

---

**🎯 Готово! Ваш бот запущен и готов к торговле!**