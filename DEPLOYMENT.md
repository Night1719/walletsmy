# 🚀 Руководство по развертыванию BG Survey Platform

## 📋 Содержание

1. [Предварительные требования](#предварительные-требования)
2. [Локальная разработка](#локальная-разработка)
3. [Продакшен развертывание](#продакшен-развертывание)
4. [Docker развертывание](#docker-развертывание)
5. [Настройка SSL](#настройка-ssl)
6. [Мониторинг и логирование](#мониторинг-и-логирование)
7. [Резервное копирование](#резервное-копирование)
8. [Обновление системы](#обновление-системы)
9. [Устранение неполадок](#устранение-неполадок)

## 🔧 Предварительные требования

### Системные требования

#### Минимальные
- **CPU**: 1 ядро
- **RAM**: 2 GB
- **Диск**: 10 GB свободного места
- **ОС**: Windows 10+, Ubuntu 18.04+, macOS 10.15+

#### Рекомендуемые
- **CPU**: 2+ ядра
- **RAM**: 4+ GB
- **Диск**: 50+ GB SSD
- **ОС**: Ubuntu 20.04+, Windows 11, macOS 12+

### Программное обеспечение

#### Обязательное
- **Python**: 3.8+
- **pip**: последняя версия
- **Git**: для клонирования репозитория

#### Для продакшена
- **Nginx**: 1.18+
- **PostgreSQL**: 12+ или MySQL 8+
- **Redis**: 6+ (для кеширования)
- **Certbot**: для SSL сертификатов

#### Для Docker
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

## 💻 Локальная разработка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd bg-survey-platform
```

### 2. Создание виртуального окружения

#### Windows
```cmd
python -m venv venv
venv\Scripts\activate
```

#### Linux/macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

```bash
cp .env.example .env
# Отредактируйте .env файл
```

### 5. Инициализация базы данных

```bash
python init_db.py
```

### 6. Создание администратора

```bash
python create_admin.py
```

### 7. Запуск приложения

```bash
python app.py
```

Приложение будет доступно по адресу: `http://localhost:5000`

## 🌐 Продакшен развертывание

### 1. Подготовка сервера

#### Обновление системы
```bash
sudo apt update && sudo apt upgrade -y
```

#### Установка необходимых пакетов
```bash
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server
```

#### Создание пользователя для приложения
```bash
sudo adduser bg-survey
sudo usermod -aG sudo bg-survey
```

### 2. Развертывание приложения

#### Клонирование в домашнюю директорию
```bash
cd /home/bg-survey
git clone <repository-url> bg-survey-platform
cd bg-survey-platform
```

#### Создание виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Настройка переменных окружения
```bash
cp .env.example .env
nano .env
```

Пример `.env` для продакшена:
```env
FLASK_CONFIG=production
SECRET_KEY=your-very-secure-secret-key-here
DATABASE_URL=postgresql://username:password@localhost/bg_survey_db
REDIS_URL=redis://localhost:6379/0
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 3. Настройка базы данных

#### PostgreSQL
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE bg_survey_db;
CREATE USER bg_survey_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE bg_survey_db TO bg_survey_user;
\q
```

#### Обновление .env
```env
DATABASE_URL=postgresql://bg_survey_user:secure_password@localhost/bg_survey_db
```

#### Инициализация базы
```bash
source venv/bin/activate
python init_db.py
python create_admin.py
```

### 4. Настройка Gunicorn

#### Создание конфигурации
```bash
python run_production.py --generate-config
```

#### Создание systemd сервиса
```bash
sudo python run_production.py --generate-systemd
```

#### Активация сервиса
```bash
sudo systemctl daemon-reload
sudo systemctl enable bg-survey-platform
sudo systemctl start bg-survey-platform
sudo systemctl status bg-survey-platform
```

### 5. Настройка Nginx

#### Создание конфигурации
```bash
sudo python run_production.py --generate-nginx
```

#### Активация конфигурации
```bash
sudo ln -s /etc/nginx/sites-available/bg-survey-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Настройка файрвола

```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## 🐳 Docker развертывание

### 1. Простое развертывание

```bash
docker-compose up -d
```

### 2. Продакшен развертывание

#### Создание .env для Docker
```env
FLASK_CONFIG=docker
SECRET_KEY=your-docker-secret-key
POSTGRES_DB=bg_survey_db
POSTGRES_USER=bg_survey_user
POSTGRES_PASSWORD=secure_password
REDIS_PASSWORD=redis_password
```

#### Запуск с продакшен конфигурацией
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 3. Масштабирование

```bash
docker-compose up -d --scale bg-survey-platform=3
```

### 4. Мониторинг контейнеров

```bash
docker-compose ps
docker-compose logs -f bg-survey-platform
```

## 🔒 Настройка SSL

### 1. Автоматическая настройка с Certbot

#### Установка Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

#### Получение сертификата
```bash
sudo certbot --nginx -d your-domain.com
```

#### Автоматическое обновление
```bash
sudo crontab -e
# Добавить строку:
0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Ручная настройка SSL

#### Создание самоподписанного сертификата
```bash
sudo mkdir -p /etc/ssl/bg-survey
cd /etc/ssl/bg-survey
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout bg-survey.key -out bg-survey.crt
```

#### Обновление Nginx конфигурации
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/bg-survey/bg-survey.crt;
    ssl_certificate_key /etc/ssl/bg-survey/bg-survey.key;
    # ... остальная конфигурация
}
```

## 📊 Мониторинг и логирование

### 1. Логирование приложения

#### Структура логов
```
logs/
├── app.log          # Основные логи приложения
├── access.log       # Логи доступа
├── error.log        # Логи ошибок
└── gunicorn.log     # Логи Gunicorn
```

#### Ротация логов
```bash
sudo nano /etc/logrotate.d/bg-survey-platform
```

```conf
/home/bg-survey/bg-survey-platform/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 bg-survey bg-survey
    postrotate
        systemctl reload bg-survey-platform
    endscript
}
```

### 2. Мониторинг системы

#### Установка мониторинга
```bash
sudo apt install -y htop iotop nethogs
```

#### Создание скрипта мониторинга
```bash
nano /home/bg-survey/monitor.sh
```

```bash
#!/bin/bash
echo "=== BG Survey Platform Status ==="
echo "Time: $(date)"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free | grep Mem | awk '{printf("%.2f%%", $3/$2 * 100.0)}')"
echo "Disk Usage: $(df -h / | awk 'NR==2 {print $5}')"
echo "Active Connections: $(netstat -an | grep :80 | wc -l)"
echo "=== Service Status ==="
systemctl status bg-survey-platform --no-pager
echo "=== Recent Logs ==="
tail -n 10 /home/bg-survey/bg-survey-platform/logs/app.log
```

#### Настройка cron для мониторинга
```bash
crontab -e
# Добавить строку:
*/5 * * * * /home/bg-survey/monitor.sh >> /home/bg-survey/monitoring.log 2>&1
```

## 💾 Резервное копирование

### 1. Автоматическое резервное копирование

#### Создание скрипта резервного копирования
```bash
nano /home/bg-survey/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/bg-survey/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="bg_survey_backup_$DATE"

# Создание директории для резервных копий
mkdir -p $BACKUP_DIR

# Резервное копирование базы данных
pg_dump -h localhost -U bg_survey_user bg_survey_db > $BACKUP_DIR/${BACKUP_NAME}.sql

# Резервное копирование файлов приложения
tar -czf $BACKUP_DIR/${BACKUP_NAME}.tar.gz -C /home/bg-survey bg-survey-platform

# Удаление резервных копий старше 30 дней
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_NAME"
```

#### Настройка автоматического запуска
```bash
chmod +x /home/bg-survey/backup.sh
crontab -e
# Добавить строку:
0 2 * * * /home/bg-survey/backup.sh >> /home/bg-survey/backup.log 2>&1
```

### 2. Восстановление из резервной копии

#### Восстановление базы данных
```bash
psql -h localhost -U bg_survey_user -d bg_survey_db < backup_file.sql
```

#### Восстановление файлов
```bash
tar -xzf backup_file.tar.gz -C /home/bg-survey/
```

## 🔄 Обновление системы

### 1. Обновление приложения

#### Остановка сервисов
```bash
sudo systemctl stop bg-survey-platform
sudo systemctl stop nginx
```

#### Создание резервной копии
```bash
/home/bg-survey/backup.sh
```

#### Обновление кода
```bash
cd /home/bg-survey/bg-survey-platform
git pull origin main
```

#### Обновление зависимостей
```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### Применение миграций базы данных
```bash
python -m flask db upgrade
```

#### Перезапуск сервисов
```bash
sudo systemctl start bg-survey-platform
sudo systemctl start nginx
sudo systemctl status bg-survey-platform
```

### 2. Откат изменений

```bash
cd /home/bg-survey/bg-survey-platform
git log --oneline -10
git checkout <commit-hash>
sudo systemctl restart bg-survey-platform
```

## 🚨 Устранение неполадок

### 1. Частые проблемы

#### Приложение не запускается
```bash
# Проверка логов
sudo journalctl -u bg-survey-platform -f

# Проверка статуса
sudo systemctl status bg-survey-platform

# Проверка портов
sudo netstat -tlnp | grep :8000
```

#### Проблемы с базой данных
```bash
# Проверка подключения
psql -h localhost -U bg_survey_user -d bg_survey_db

# Проверка логов PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-*.log
```

#### Проблемы с Nginx
```bash
# Проверка конфигурации
sudo nginx -t

# Проверка логов
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 2. Диагностические команды

#### Проверка системы
```bash
# Статус всех сервисов
sudo systemctl status bg-survey-platform nginx postgresql redis

# Использование ресурсов
htop
df -h
free -h

# Сетевые соединения
netstat -tlnp
ss -tlnp
```

#### Проверка приложения
```bash
# Тест подключения к базе данных
python -c "from app import db; print('Database connection OK')"

# Проверка переменных окружения
python -c "import os; print('FLASK_CONFIG:', os.getenv('FLASK_CONFIG'))"
```

### 3. Восстановление после сбоя

#### Автоматический перезапуск
```bash
sudo systemctl enable bg-survey-platform
sudo systemctl enable nginx
sudo systemctl enable postgresql
sudo systemctl enable redis
```

#### Мониторинг и уведомления
```bash
# Установка утилиты для уведомлений
sudo apt install -y mailutils

# Настройка уведомлений по email
echo "Subject: BG Survey Platform Alert" | sendmail admin@company.com
```

## 📞 Поддержка

### Контакты для поддержки
- **Техническая поддержка**: tech-support@buntergroup.com
- **Документация**: https://docs.bg-survey-platform.com
- **GitHub Issues**: https://github.com/buntergroup/bg-survey-platform/issues

### Полезные ресурсы
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**BG Survey Platform** - профессиональное решение для корпоративных опросов.

*Версия 1.0.0 | Последнее обновление: 2024*