# 🌐 Настройка Mini App для работы в интернете

## 📋 **Варианты настройки внешнего доступа**

### **Вариант 1: ngrok (Быстрый тест) - РЕКОМЕНДУЕТСЯ для начала**

#### **Шаг 1: Установка ngrok**
1. Скачайте ngrok с https://ngrok.com/download
2. Распакуйте в папку (например, `C:\ngrok\`)
3. Зарегистрируйтесь и получите токен

#### **Шаг 2: Настройка ngrok**
```cmd
# Установите токен
ngrok config add-authtoken YOUR_AUTHTOKEN

# Запустите туннель на порт 4477
ngrok http 4477
```

#### **Шаг 3: Обновите конфигурацию**
После запуска ngrok вы получите URL вида: `https://abc123.ngrok.io`

Обновите файл `.env`:
```env
MINIAPP_URL=https://abc123.ngrok.io/miniapp
MINIAPP_WEBHOOK_URL=https://abc123.ngrok.io
MINIAPP_MODE=remote
```

#### **Шаг 4: Запуск**
```cmd
# Терминал 1: Mini App
cd TGBOT\miniapp
python run.py

# Терминал 2: ngrok
ngrok http 4477

# Терминал 3: Бот
cd TGBOT
python bot.py
```

---

### **Вариант 2: VPS/Сервер (Постоянное решение)**

#### **Шаг 1: Настройка сервера**
```bash
# Установка Python и зависимостей
sudo apt update
sudo apt install python3 python3-pip nginx

# Установка SSL сертификата (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
```

#### **Шаг 2: Настройка Nginx**
Создайте файл `/etc/nginx/sites-available/miniapp`:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:4477;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### **Шаг 3: Активация сайта**
```bash
sudo ln -s /etc/nginx/sites-available/miniapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### **Шаг 4: SSL сертификат**
```bash
sudo certbot --nginx -d your-domain.com
```

#### **Шаг 5: Настройка .env на сервере**
```env
MINIAPP_URL=https://your-domain.com/miniapp
MINIAPP_WEBHOOK_URL=https://your-domain.com
MINIAPP_MODE=remote
```

---

### **Вариант 3: Docker + Docker Compose (Профессиональное решение)**

#### **Шаг 1: Создайте docker-compose.prod.yml**
```yaml
version: '3.8'
services:
  miniapp:
    build: ./miniapp
    ports:
      - "4477:4477"
    environment:
      - MINIAPP_URL=https://your-domain.com/miniapp
      - MINIAPP_WEBHOOK_URL=https://your-domain.com
      - MINIAPP_MODE=remote
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - miniapp
    restart: unless-stopped
```

#### **Шаг 2: Запуск**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔧 **Настройка бота для работы с внешним Mini App**

### **1. Обновите .env файл бота:**
```env
# === Основные настройки ===
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_USER_IDS=your_telegram_id

# === Mini App (внешний доступ) ===
MINIAPP_URL=https://your-domain.com:4477/miniapp
MINIAPP_WEBHOOK_URL=https://your-domain.com:4477
MINIAPP_MODE=remote
LINK_EXPIRY_MINUTES=40

# === SMTP для OTP ===
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
SMTP_FROM=your_email@gmail.com
CORP_EMAIL_DOMAIN=yourcompany.com
```

### **2. Настройка Telegram Webhook (если используете)**
```python
# В bot.py добавьте настройку webhook
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

async def on_startup(dispatcher, bot):
    # Настройка webhook для Mini App
    webhook_url = f"{MINIAPP_WEBHOOK_URL}/webhook"
    await bot.set_webhook(webhook_url)
    print(f"Webhook set to: {webhook_url}")
```

---

## 🚀 **Быстрый старт с ngrok**

### **1. Скачайте и установите ngrok:**
- Перейдите на https://ngrok.com/download
- Скачайте версию для Windows
- Распакуйте в папку `C:\ngrok\`

### **2. Зарегистрируйтесь и получите токен:**
- Создайте аккаунт на https://ngrok.com
- Скопируйте токен из панели управления

### **3. Настройте ngrok:**
```cmd
cd C:\ngrok
ngrok config add-authtoken YOUR_AUTHTOKEN
```

### **4. Запустите все сервисы:**

**Терминал 1 - Mini App:**
```cmd
cd TGBOT\miniapp
python run.py
```

**Терминал 2 - ngrok:**
```cmd
cd C:\ngrok
ngrok http 4477
```

**Терминал 3 - Бот:**
```cmd
cd TGBOT
python bot.py
```

### **5. Скопируйте URL из ngrok:**
После запуска ngrok вы увидите:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:4477
```

### **6. Обновите .env:**
```env
MINIAPP_URL=https://abc123.ngrok.io/miniapp
MINIAPP_WEBHOOK_URL=https://abc123.ngrok.io
MINIAPP_MODE=remote
```

### **7. Перезапустите бота:**
```cmd
python bot.py
```

---

## ✅ **Проверка работы**

1. **Откройте браузер** и перейдите по адресу из ngrok
2. **Запустите бота** и нажмите "📚 Инструкции"
3. **Пройдите OTP** по email
4. **Выберите инструкцию** - должен открыться Mini App в интернете

---

## 🔍 **Устранение проблем**

### **Проблема: "ngrok not found"**
```cmd
# Добавьте ngrok в PATH или используйте полный путь
C:\ngrok\ngrok.exe http 4477
```

### **Проблема: "Connection refused"**
- Убедитесь, что Mini App запущен на порту 4477
- Проверьте, что ngrok подключен к правильному порту

### **Проблема: "SSL certificate error"**
- ngrok автоматически предоставляет SSL
- Для собственного домена настройте Let's Encrypt

### **Проблема: "Mini App не открывается"**
- Проверьте URL в .env файле
- Убедитесь, что ngrok туннель активен
- Проверьте логи бота на ошибки

---

## 🎯 **Рекомендации**

1. **Для тестирования:** используйте ngrok
2. **Для продакшена:** настройте VPS с доменом и SSL
3. **Для разработки:** используйте Docker Compose
4. **Всегда используйте HTTPS** для Mini App в интернете

Теперь Mini App будет доступен из интернета! 🌐