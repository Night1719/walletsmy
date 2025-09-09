# 🪟 Полная настройка для Windows - Бот + Mini App

## 📋 **Системные требования**

- **Windows 10/11**
- **Python 3.8+** (скачать с https://python.org)
- **Git** (опционально, для клонирования)
- **Ваш домен** (для внешнего доступа)

---

## 🚀 **Шаг 1: Установка Python**

### **1.1 Скачайте Python:**
- Перейдите на https://python.org/downloads/
- Скачайте Python 3.8+ для Windows
- **ВАЖНО:** При установке отметьте "Add Python to PATH"

### **1.2 Проверьте установку:**
```cmd
python --version
pip --version
```

---

## 🔧 **Шаг 2: Настройка проекта**

### **2.1 Создайте папку проекта:**
```cmd
mkdir C:\TelegramBot
cd C:\TelegramBot
```

### **2.2 Скопируйте файлы проекта** в папку `C:\TelegramBot\`

### **2.3 Создайте виртуальное окружение:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### **2.4 Установите зависимости:**
```cmd
pip install -r requirements.txt
cd miniapp
pip install -r requirements.txt
cd ..
```

---

## ⚙️ **Шаг 3: Настройка конфигурации**

### **3.1 Создайте файл `.env` в папке `C:\TelegramBot\`:**
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

# === Остальные настройки ===
INTRASERVICE_BASE_URL=
INTRASERVICE_USER=
INTRASERVICE_PASS=
API_USER_ID=
```

### **3.2 Заполните ваши данные:**
- `TELEGRAM_BOT_TOKEN` - токен вашего бота от @BotFather
- `ADMIN_USER_IDS` - ваш Telegram ID (узнать у @userinfobot)
- `your-domain.com` - замените на ваш домен
- Настройки SMTP для отправки OTP

---

## 🌐 **Шаг 4: Настройка для внешнего доступа**

### **4.1 Вариант A: ngrok (Быстрый тест)**

#### **Установка ngrok:**
1. Скачайте ngrok с https://ngrok.com/download
2. Распакуйте в `C:\ngrok\`
3. Зарегистрируйтесь и получите токен
4. Выполните: `C:\ngrok\ngrok.exe config add-authtoken YOUR_TOKEN`

#### **Запуск с ngrok:**
```cmd
# Терминал 1: Mini App
cd C:\TelegramBot\miniapp
python run.py

# Терминал 2: ngrok
C:\ngrok\ngrok.exe http 4477

# Терминал 3: Бот
cd C:\TelegramBot
python bot.py
```

### **4.2 Вариант B: Ваш домен (Постоянное решение)**

#### **Настройка Nginx на Windows:**
1. Скачайте Nginx для Windows с http://nginx.org/en/download.html
2. Распакуйте в `C:\nginx\`
3. Создайте файл `C:\nginx\conf\nginx.conf`:

```nginx
worker_processes  1;

events {
    worker_connections  1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    
    server {
        listen       80;
        server_name  your-domain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name:4477$request_uri;
    }
    
    server {
        listen       443 ssl;
        server_name  your-domain.com:4477;
        
        # SSL Configuration (замените на ваши сертификаты)
        ssl_certificate      C:/path/to/your/cert.pem;
        ssl_certificate_key  C:/path/to/your/private.key;
        
        # Mini App routes
        location /miniapp {
            proxy_pass http://localhost:4477;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # API routes
        location /api/ {
            proxy_pass http://localhost:4477;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

#### **Запуск Nginx:**
```cmd
cd C:\nginx
nginx.exe
```

---

## 🚀 **Шаг 5: Запуск приложения**

### **5.1 Создайте скрипты запуска:**

#### **start_bot.bat:**
```batch
@echo off
cd /d C:\TelegramBot
call venv\Scripts\activate
python bot.py
pause
```

#### **start_miniapp.bat:**
```batch
@echo off
cd /d C:\TelegramBot\miniapp
call ..\venv\Scripts\activate
python run.py
pause
```

#### **start_ngrok.bat:**
```batch
@echo off
C:\ngrok\ngrok.exe http 4477
pause
```

### **5.2 Запуск всех сервисов:**

#### **Для тестирования с ngrok:**
1. Запустите `start_miniapp.bat`
2. Запустите `start_ngrok.bat`
3. Скопируйте URL из ngrok (например: `https://abc123.ngrok.io`)
4. Обновите `.env` файл:
   ```env
   MINIAPP_URL=https://abc123.ngrok.io/miniapp
   MINIAPP_WEBHOOK_URL=https://abc123.ngrok.io
   ```
5. Запустите `start_bot.bat`

#### **Для продакшена с доменом:**
1. Запустите Nginx: `C:\nginx\nginx.exe`
2. Запустите `start_miniapp.bat`
3. Запустите `start_bot.bat`

---

## 🔧 **Шаг 6: Настройка как службы Windows (опционально)**

### **6.1 Установка NSSM:**
1. Скачайте NSSM с https://nssm.cc/download
2. Распакуйте в `C:\nssm\`

### **6.2 Создание службы для бота:**
```cmd
C:\nssm\win64\nssm.exe install TelegramBot C:\TelegramBot\venv\Scripts\python.exe C:\TelegramBot\bot.py
C:\nssm\win64\nssm.exe start TelegramBot
```

### **6.3 Создание службы для Mini App:**
```cmd
C:\nssm\win64\nssm.exe install MiniApp C:\TelegramBot\venv\Scripts\python.exe C:\TelegramBot\miniapp\run.py
C:\nssm\win64\nssm.exe start MiniApp
```

---

## 📱 **Шаг 7: Добавление инструкций**

### **7.1 Через админ панель бота:**
1. Запустите бота
2. Нажмите "🔧 Админ панель"
3. "📁 Категории" → "➕ Добавить категорию"
4. "📋 Инструкции" → выберите категорию → "➕ Добавить инструкцию"
5. Выберите формат (PDF, DOCX, MP4, AVI, MOV)
6. Отправьте файл в чат

### **7.2 Прямая загрузка файлов:**
Создайте структуру папок:
```
C:\TelegramBot\instructions\
├── 1c\
│   ├── ar2.pdf
│   └── dm.docx
├── email\
│   ├── iphone.mp4
│   ├── android.mp4
│   └── outlook.pdf
```

---

## ✅ **Проверка работы**

### **1. Проверка Mini App:**
- **Локально:** `http://localhost:4477/miniapp`
- **В интернете:** `https://your-domain.com:4477/miniapp` или ngrok URL

### **2. Проверка бота:**
1. Найдите бота в Telegram
2. Нажмите `/start`
3. Авторизуйтесь
4. Нажмите "📚 Инструкции"
5. Введите email для OTP
6. Выберите инструкцию
7. Должен открыться Mini App

---

## 🔍 **Устранение проблем**

### **Проблема: "Python not found"**
- Переустановите Python с отметкой "Add Python to PATH"
- Перезапустите командную строку

### **Проблема: "Module not found"**
```cmd
cd C:\TelegramBot
venv\Scripts\activate
pip install -r requirements.txt
```

### **Проблема: "Port 4477 already in use"**
```cmd
netstat -ano | findstr :4477
taskkill /PID <PID> /F
```

### **Проблема: "Mini App not opening"**
- Проверьте URL в .env файле
- Убедитесь, что Mini App запущен на порту 4477
- Проверьте настройки Nginx (если используете)

### **Проблема: "SMTP error"**
- Проверьте настройки SMTP в .env
- Используйте App Password для Gmail
- Проверьте домен в `CORP_EMAIL_DOMAIN`

---

## 🎯 **Готово!**

Теперь у вас есть:
- ✅ Бот работает на Windows
- ✅ Mini App работает на Windows на порту 4477
- ✅ Доступ из интернета через ваш домен или ngrok
- ✅ Поддержка видео-инструкций
- ✅ Админ панель для управления
- ✅ OTP авторизация по email

**Ваш Mini App доступен по адресу:** `https://your-domain.com:4477/miniapp` 🎉