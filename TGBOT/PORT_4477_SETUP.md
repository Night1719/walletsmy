# 🌐 Настройка Mini App на порту 4477 для внешнего доступа

## 📋 **Настройка для вашего домена на порту 4477**

### **1. Обновите .env файл:**
```env
# === Основные настройки ===
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_USER_IDS=your_telegram_id

# === Mini App (ваш домен на порту 4477) ===
MINIAPP_URL=https://your-domain.com:4477/miniapp
MINIAPP_WEBHOOK_URL=https://your-domain.com:4477
MINIAPP_MODE=remote
LINK_EXPIRY_MINUTES=40

# === Поддержка видео ===
ALLOWED_FILE_EXTENSIONS=pdf,docx,doc,txt,mp4,avi,mov,wmv,flv,webm,mkv
MAX_FILE_SIZE_MB=100
VIDEO_FILE_EXTENSIONS=mp4,avi,mov,wmv,flv,webm,mkv

# === SMTP для OTP ===
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
SMTP_FROM=your_email@gmail.com
CORP_EMAIL_DOMAIN=yourcompany.com
```

### **2. Настройка Nginx для порта 4477:**

Создайте файл `/etc/nginx/sites-available/miniapp-4477`:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name:4477$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com:4477;
    
    # SSL Configuration
    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/private.key;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Mini App routes
    location /miniapp {
        proxy_pass http://localhost:4477;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings for large files
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # API routes
    location /api/ {
        proxy_pass http://localhost:4477;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers for API
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
    }
    
    # Root redirect to miniapp
    location / {
        return 301 https://$server_name:4477/miniapp;
    }
}
```

### **3. Альтернативная настройка (прямой доступ к порту 4477):**

Если вы хотите, чтобы Mini App был доступен напрямую на порту 4477:

```nginx
# В файле /etc/nginx/sites-available/miniapp-direct
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name:4477$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com:4477;
    
    # SSL Configuration
    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/private.key;
    
    # Direct proxy to Mini App
    location / {
        proxy_pass http://localhost:4477;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings for large files
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### **4. Активация сайта:**
```bash
sudo ln -s /etc/nginx/sites-available/miniapp-4477 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### **5. SSL сертификат для порта 4477:**
```bash
# Для Let's Encrypt с портом
sudo certbot --nginx -d your-domain.com --nginx-server-root /etc/nginx --nginx-ctl /usr/sbin/nginx
```

### **6. Настройка файрвола:**
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 4477  # Открываем порт 4477
sudo ufw enable
```

---

## 🚀 **Развертывание на сервере**

### **1. Подготовка сервера:**
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и зависимостей
sudo apt install python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

# Создание пользователя для приложения
sudo useradd -m -s /bin/bash miniapp
sudo usermod -aG www-data miniapp
```

### **2. Загрузка и настройка приложения:**
```bash
# Переключение на пользователя miniapp
sudo su - miniapp

# Создание директории приложения
mkdir -p /home/miniapp/app
cd /home/miniapp/app

# Загрузка файлов (скопируйте файлы проекта)
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### **3. Создание systemd сервиса:**
Создайте файл `/etc/systemd/system/miniapp-4477.service`:
```ini
[Unit]
Description=Telegram Mini App on Port 4477
After=network.target

[Service]
Type=simple
User=miniapp
Group=miniapp
WorkingDirectory=/home/miniapp/app
Environment=PATH=/home/miniapp/app/venv/bin
Environment=MINIAPP_PORT=4477
ExecStart=/home/miniapp/app/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **4. Запуск сервиса:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable miniapp-4477
sudo systemctl start miniapp-4477
sudo systemctl status miniapp-4477
```

---

## 🔧 **Настройка для локальной разработки**

### **1. Локальный запуск:**
```cmd
cd TGBOT\miniapp
python run.py
```
Mini App запустится на `http://localhost:4477`

### **2. Настройка .env для локальной разработки:**
```env
MINIAPP_URL=http://localhost:4477/miniapp
MINIAPP_WEBHOOK_URL=http://localhost:4477
MINIAPP_MODE=local
```

### **3. Тестирование с ngrok:**
```cmd
ngrok http 4477
```
После запуска ngrok обновите .env:
```env
MINIAPP_URL=https://abc123.ngrok.io/miniapp
MINIAPP_WEBHOOK_URL=https://abc123.ngrok.io
MINIAPP_MODE=remote
```

---

## ✅ **Проверка работы**

### **1. Проверка Mini App:**
- **Локально:** `http://localhost:4477/miniapp`
- **В интернете:** `https://your-domain.com:4477/miniapp`

### **2. Проверка API:**
```bash
curl -X GET "https://your-domain.com:4477/api/instructions/test"
```

### **3. Проверка бота:**
1. Запустите бота
2. Нажмите "📚 Инструкции"
3. Пройдите OTP по email
4. Выберите категорию и инструкцию
5. Должен открыться Mini App с видео

---

## 🔍 **Устранение проблем**

### **Проблема: "Port 4477 not accessible"**
- Проверьте файрвол: `sudo ufw status`
- Убедитесь, что порт открыт: `sudo ufw allow 4477`
- Проверьте, что сервис запущен: `sudo systemctl status miniapp-4477`

### **Проблема: "SSL certificate error"**
- Обновите SSL сертификат: `sudo certbot renew`
- Проверьте настройки Nginx для порта 4477

### **Проблема: "Mini App not opening"**
- Проверьте URL в .env файле
- Убедитесь, что сервис запущен: `sudo systemctl status miniapp-4477`
- Проверьте логи: `sudo journalctl -u miniapp-4477 -f`

---

## 🎯 **Готово!**

Теперь у вас есть:
- ✅ Mini App на порту 4477
- ✅ Доступ из интернета: `https://your-domain.com:4477/miniapp`
- ✅ Поддержка видео-инструкций
- ✅ Безопасный доступ через OTP
- ✅ Админ панель для управления

**Ваш Mini App доступен по адресу:** `https://your-domain.com:4477/miniapp` 🎉