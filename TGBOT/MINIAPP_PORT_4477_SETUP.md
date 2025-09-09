# 🚀 Настройка Mini App на порт 4477

## 📋 **Пошаговая инструкция запуска Mini App**

### **Шаг 1: Подготовка**

1. **Убедитесь, что Python 3.8+ установлен:**
   ```cmd
   python --version
   ```

2. **Перейдите в папку Mini App:**
   ```cmd
   cd TGBOT\miniapp
   ```

### **Шаг 2: Установка зависимостей**

```cmd
pip install -r requirements.txt
```

### **Шаг 3: Настройка конфигурации**

Создайте файл `.env` в папке `TGBOT` (не в miniapp):

```env
# === Основные настройки ===
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_USER_IDS=your_telegram_id

# === Mini App (порт 4477) ===
MINIAPP_URL=http://localhost:4477/miniapp
MINIAPP_WEBHOOK_URL=http://localhost:4477
MINIAPP_MODE=local
LINK_EXPIRY_MINUTES=40

# === SMTP для OTP ===
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
SMTP_FROM=your_email@gmail.com
CORP_EMAIL_DOMAIN=yourcompany.com
```

### **Шаг 4: Запуск Mini App**

#### **Вариант A: Через Python (рекомендуется)**
```cmd
cd TGBOT\miniapp
python run.py
```

#### **Вариант B: Через Windows скрипт**
```cmd
cd TGBOT\miniapp
run_windows.bat
```

#### **Вариант C: Через PowerShell**
```cmd
cd TGBOT\miniapp
.\run_windows.ps1
```

### **Шаг 5: Проверка работы**

1. **Mini App должен запуститься на:** `http://localhost:4477`
2. **Основная страница:** `http://localhost:4477/miniapp`
3. **В логах должно быть:**
   ```
   Starting Mini App on 0.0.0.0:4477
   Debug mode: True
   ```

### **Шаг 6: Запуск бота**

В **другом терминале**:
```cmd
cd TGBOT
python bot.py
```

## 🔧 **Добавление инструкций через админ панель**

### **Шаг 1: Откройте админ панель**

1. Запустите бота
2. Нажмите "🔧 Админ панель"
3. Убедитесь, что ваш ID в `ADMIN_USER_IDS`

### **Шаг 2: Создание категории**

1. Нажмите "📁 Категории"
2. Нажмите "➕ Добавить категорию"
3. Введите ID категории (например: `network`)
4. Введите название (например: `Сеть`)
5. Введите иконку (например: `🌐`)

### **Шаг 3: Добавление инструкции**

1. Нажмите "📋 Инструкции"
2. Выберите категорию
3. Нажмите "➕ Добавить инструкцию"
4. Введите название инструкции
5. Введите описание
6. Выберите формат файла (PDF, DOCX, DOC, TXT)
7. Отправьте файл в чат

## 🌐 **Настройка для интернета (порт 4477)**

### **Вариант 1: Nginx + SSL**

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /miniapp {
        proxy_pass http://localhost:4477;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **Вариант 2: ngrok (для тестирования)**

```cmd
ngrok http 4477
```

Затем обновите `.env`:
```env
MINIAPP_URL=https://your-ngrok-url.ngrok.io/miniapp
MINIAPP_WEBHOOK_URL=https://your-ngrok-url.ngrok.io
```

## 🔍 **Проверка работы**

1. **Запустите Mini App** на порту 4477
2. **Запустите бота**
3. **Нажмите "📚 Инструкции"**
4. **Введите email** для OTP
5. **Введите код** из email
6. **Выберите категорию** и инструкцию
7. **Откроется Mini App** с файлом

## ❌ **Устранение проблем**

### **Проблема: "Port 4477 already in use"**
```cmd
netstat -ano | findstr :4477
taskkill /PID <PID> /F
```

### **Проблема: "Module not found"**
```cmd
pip install -r requirements.txt
```

### **Проблема: "SMTP error"**
- Проверьте настройки SMTP
- Используйте App Password для Gmail
- Проверьте домен в `CORP_EMAIL_DOMAIN`

## ✅ **Готово!**

Теперь Mini App работает на порту 4477 и готов к использованию! 🎉