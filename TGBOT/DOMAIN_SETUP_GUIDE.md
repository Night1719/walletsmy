# 🌐 Настройка Mini App для вашего домена с поддержкой видео

## 📋 **Настройка для вашего домена**

### **1. Обновите .env файл:**
```env
# === Основные настройки ===
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_USER_IDS=your_telegram_id

# === Mini App (ваш домен) ===
MINIAPP_URL=https://your-domain.com/miniapp
MINIAPP_WEBHOOK_URL=https://your-domain.com
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

### **2. Настройка Nginx для вашего домена:**

Создайте файл `/etc/nginx/sites-available/miniapp`:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
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
    
    # Static files (if any)
    location /static/ {
        alias /path/to/your/static/files/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### **3. Активация сайта:**
```bash
sudo ln -s /etc/nginx/sites-available/miniapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### **4. SSL сертификат (Let's Encrypt):**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### **5. Настройка файрвола:**
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

---

## 🎥 **Поддержка видео-инструкций**

### **Поддерживаемые форматы:**
- **MP4** - рекомендуется для веб-просмотра
- **AVI** - старый формат
- **MOV** - Apple QuickTime
- **WMV** - Windows Media
- **FLV** - Flash Video
- **WebM** - современный веб-формат
- **MKV** - Matroska Video

### **Рекомендации по видео:**
1. **Формат:** MP4 с кодеком H.264
2. **Разрешение:** 1280x720 (HD) или 1920x1080 (Full HD)
3. **Битрейт:** 1-2 Mbps для HD, 2-4 Mbps для Full HD
4. **Длительность:** до 10 минут для быстрой загрузки
5. **Размер файла:** до 100 MB

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
Создайте файл `/etc/systemd/system/miniapp.service`:
```ini
[Unit]
Description=Telegram Mini App
After=network.target

[Service]
Type=simple
User=miniapp
Group=miniapp
WorkingDirectory=/home/miniapp/app
Environment=PATH=/home/miniapp/app/venv/bin
ExecStart=/home/miniapp/app/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **4. Запуск сервиса:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable miniapp
sudo systemctl start miniapp
sudo systemctl status miniapp
```

---

## 🔧 **Добавление видео-инструкций**

### **1. Через админ панель бота:**
1. Нажмите "🔧 Админ панель"
2. "📁 Категории" → "➕ Добавить категорию"
3. "📋 Инструкции" → выберите категорию → "➕ Добавить инструкцию"
4. Выберите формат видео (MP4, AVI, MOV)
5. Отправьте видео файл в чат

### **2. Прямая загрузка на сервер:**
```bash
# Создание директории для инструкций
sudo mkdir -p /home/miniapp/app/instructions
sudo chown -R miniapp:miniapp /home/miniapp/app/instructions

# Загрузка видео файла
sudo cp your_video.mp4 /home/miniapp/app/instructions/category_name/instruction_name.mp4
```

---

## ✅ **Проверка работы**

### **1. Проверка Mini App:**
- Откройте `https://your-domain.com/miniapp` в браузере
- Должна загрузиться страница Mini App

### **2. Проверка API:**
```bash
curl -X GET "https://your-domain.com/api/instructions/test"
```

### **3. Проверка бота:**
1. Запустите бота
2. Нажмите "📚 Инструкции"
3. Пройдите OTP по email
4. Выберите категорию и инструкцию
5. Должен открыться Mini App с видео

---

## 🔍 **Устранение проблем**

### **Проблема: "Video not loading"**
- Проверьте формат видео (должен быть MP4, AVI, MOV)
- Убедитесь, что файл не поврежден
- Проверьте размер файла (максимум 100 MB)

### **Проблема: "SSL certificate error"**
- Обновите SSL сертификат: `sudo certbot renew`
- Проверьте настройки Nginx

### **Проблема: "Mini App not opening"**
- Проверьте URL в .env файле
- Убедитесь, что сервис запущен: `sudo systemctl status miniapp`
- Проверьте логи: `sudo journalctl -u miniapp -f`

---

## 🎯 **Готово!**

Теперь у вас есть:
- ✅ Mini App на вашем домене
- ✅ Поддержка видео-инструкций
- ✅ Безопасный доступ через OTP
- ✅ Админ панель для управления

**Ваш Mini App доступен по адресу:** `https://your-domain.com/miniapp` 🎉