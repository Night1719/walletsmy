# 🔒 Руководство по безопасному развертыванию BG Survey Platform

## ⚠️ КРИТИЧЕСКИ ВАЖНО

Перед развертыванием в интернете **ОБЯЗАТЕЛЬНО** выполните все пункты этого руководства!

## 🛡️ Меры безопасности

### 1. Переменные окружения

Создайте файл `.env` с безопасными настройками:

```bash
# Критически важные настройки
SECRET_KEY=your-super-secret-key-here-32-chars-minimum
DATABASE_URL=postgresql://user:password@localhost/surveys
REDIS_URL=redis://localhost:6379/0

# SSL настройки
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem

# Дополнительные настройки безопасности
IP_WHITELIST=192.168.1.0/24,10.0.0.0/8  # Опционально
LOG_LEVEL=WARNING
```

### 2. Генерация безопасного SECRET_KEY

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Настройка базы данных

**НЕ ИСПОЛЬЗУЙТЕ SQLite в продакшене!**

```bash
# PostgreSQL
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres createdb surveys
sudo -u postgres createuser survey_user
sudo -u postgres psql -c "ALTER USER survey_user PASSWORD 'strong_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE surveys TO survey_user;"
```

### 4. Настройка Redis (для rate limiting)

```bash
sudo apt-get install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 5. SSL сертификаты

#### Let's Encrypt (рекомендуется)
```bash
sudo apt-get install certbot
sudo certbot certonly --standalone -d your-domain.com
```

#### Самоподписанный сертификат (только для тестирования)
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

### 6. Настройка Nginx

Создайте файл `/etc/nginx/sites-available/survey-platform`:

```nginx
upstream survey_app {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL сертификаты
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    
    # Заголовки безопасности
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
    
    location / {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://survey_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /login {
        limit_req zone=login burst=3 nodelay;
        proxy_pass http://survey_app;
    }
}
```

Активируйте конфигурацию:
```bash
sudo ln -s /etc/nginx/sites-available/survey-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. Настройка файрвола

```bash
# UFW
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 5000/tcp   # Блокируем прямой доступ к Flask

# iptables (альтернатива)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 5000 -j DROP
```

### 8. Настройка systemd сервиса

Создайте файл `/etc/systemd/system/survey-platform.service`:

```ini
[Unit]
Description=BG Survey Platform
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/venv/bin
EnvironmentFile=/path/to/your/.env
ExecStart=/path/to/your/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активируйте сервис:
```bash
sudo systemctl daemon-reload
sudo systemctl enable survey-platform
sudo systemctl start survey-platform
```

### 9. Мониторинг и логирование

```bash
# Просмотр логов
sudo journalctl -u survey-platform -f

# Логи безопасности
tail -f security.log

# Логи приложения
tail -f app.log

# Мониторинг ресурсов
htop
df -h
free -h
```

### 10. Резервное копирование

Создайте скрипт резервного копирования `/usr/local/bin/backup-survey.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/survey-platform"
mkdir -p $BACKUP_DIR

# Резервная копия базы данных
pg_dump surveys > $BACKUP_DIR/surveys_$DATE.sql

# Резервная копия файлов
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /path/to/your/app

# Удаляем старые резервные копии (старше 30 дней)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

Сделайте скрипт исполняемым и добавьте в crontab:
```bash
chmod +x /usr/local/bin/backup-survey.sh
crontab -e
# Добавьте: 0 2 * * * /usr/local/bin/backup-survey.sh
```

## 🚨 Чек-лист безопасности

- [ ] ✅ SECRET_KEY сгенерирован и установлен
- [ ] ✅ База данных PostgreSQL настроена
- [ ] ✅ Redis установлен и запущен
- [ ] ✅ SSL сертификаты настроены
- [ ] ✅ Nginx сконфигурирован
- [ ] ✅ Файрвол настроен
- [ ] ✅ Systemd сервис создан
- [ ] ✅ Логирование настроено
- [ ] ✅ Резервное копирование настроено
- [ ] ✅ Мониторинг настроен

## 🔍 Проверка безопасности

### Тестирование SSL
```bash
# Проверка SSL
openssl s_client -connect your-domain.com:443

# Проверка заголовков безопасности
curl -I https://your-domain.com
```

### Тестирование rate limiting
```bash
# Тест лимитов входа
for i in {1..10}; do curl -X POST https://your-domain.com/login; done
```

### Сканирование уязвимостей
```bash
# Установка сканера
pip install safety bandit

# Проверка зависимостей
safety check

# Статический анализ кода
bandit -r .
```

## 📊 Мониторинг производительности

```bash
# Установка мониторинга
pip install psutil

# Мониторинг в реальном времени
watch -n 1 'ps aux | grep python'
```

## 🆘 В случае атаки

1. **Немедленно заблокируйте IP:**
   ```bash
   sudo iptables -A INPUT -s ATTACKER_IP -j DROP
   ```

2. **Проверьте логи:**
   ```bash
   tail -f security.log | grep ATTACKER_IP
   ```

3. **Перезапустите сервисы:**
   ```bash
   sudo systemctl restart survey-platform
   sudo systemctl restart nginx
   ```

4. **Смените пароли и ключи:**
   ```bash
   # Сгенерируйте новый SECRET_KEY
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

## 📞 Контакты для экстренных случаев

- Администратор системы: admin@your-domain.com
- Техническая поддержка: support@your-domain.com
- Телефон: +7-XXX-XXX-XXXX

---

**⚠️ ВАЖНО: Этот документ содержит критически важную информацию для безопасности. Храните его в безопасном месте и не публикуйте в открытом доступе!**