# 🚀 Telegram Bot with Dynamic Instructions - Download Package

## 📦 **Скачать проект:**

### **ZIP архив (рекомендуется):**
- `TGBOT_dynamic_instructions.zip` - Полный проект в ZIP формате

### **TAR.GZ архив:**
- `TGBOT_dynamic_instructions.tar.gz` - Полный проект в TAR.GZ формате

## 🌟 **Что включено в проект:**

### **🔧 Основные возможности:**
- ✅ **Динамическое управление инструкциями** через Telegram
- ✅ **Админская панель** для добавления новых инструкций
- ✅ **Telegram Mini App** для безопасного просмотра файлов
- ✅ **Система безопасных ссылок** с временным доступом (40 минут)
- ✅ **Загрузка файлов** PDF, DOCX, DOC через Telegram
- ✅ **Автоматическое создание** структуры папок
- ✅ **Валидация файлов** и проверка безопасности

### **📁 Структура проекта:**
```
TGBOT/
├── bot.py                          # Основной файл бота
├── instruction_manager.py          # Система управления инструкциями
├── handlers/admin.py               # Админский интерфейс
├── miniapp/                        # Telegram Mini App
│   ├── app.py                      # Flask приложение
│   ├── secure_links.py             # Система безопасных ссылок
│   ├── templates/                  # HTML шаблоны
│   └── run_production.py           # Скрипт для продакшена
├── keyboards.py                    # Динамические клавиатуры
├── config.py                       # Конфигурация
├── requirements.txt                # Python зависимости
├── docker-compose.yml              # Docker Compose
├── .env.example                    # Пример переменных окружения
└── документация/                   # Подробная документация
```

## 🚀 **Быстрый старт:**

### **1. Распаковка:**
```bash
# Для ZIP
unzip TGBOT_dynamic_instructions.zip

# Для TAR.GZ
tar -xzf TGBOT_dynamic_instructions.tar.gz
```

### **2. Установка зависимостей:**
```bash
cd TGBOT
pip install -r requirements.txt
```

### **3. Настройка:**
```bash
# Скопировать пример конфигурации
cp .env.example .env

# Отредактировать .env файл
nano .env
```

### **4. Запуск:**
```bash
python bot.py
```

## ⚙️ **Настройка переменных окружения:**

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Admin Configuration
ADMIN_USER_IDS=123456789,987654321

# Mini App Configuration
MINIAPP_URL=https://your-domain.com/miniapp
MINIAPP_WEBHOOK_URL=https://your-domain.com
LINK_EXPIRY_MINUTES=40

# File Server (если используется)
FILE_SERVER_BASE_URL=https://files.example.com
FILE_SERVER_USER=your_file_server_user
FILE_SERVER_PASS=your_file_server_password
```

## 📚 **Документация:**

- **`DYNAMIC_INSTRUCTIONS_SUMMARY.md`** - Полное описание системы управления инструкциями
- **`SECURE_LINKS_SUMMARY.md`** - Детали системы безопасных ссылок
- **`MINIAPP_SETUP.md`** - Настройка Telegram Mini App
- **`WINDOWS_SETUP.md`** - Развертывание на Windows
- **`MINIAPP_FIXES_SUMMARY.md`** - Исправления и улучшения

## 🔧 **Основные функции:**

### **Для администраторов:**
- 📁 **Управление категориями** - создание и редактирование
- 📝 **Управление инструкциями** - добавление новых инструкций
- 📤 **Загрузка файлов** - PDF, DOCX, DOC через Telegram
- 📊 **Статистика** - просмотр использования
- ⚙️ **Настройки** - конфигурация системы

### **Для пользователей:**
- 📚 **Просмотр инструкций** - по категориям
- 🔒 **Безопасный доступ** - через временные ссылки
- 📱 **Мобильный интерфейс** - оптимизирован для Telegram
- 📄 **Просмотр файлов** - PDF с навигацией, Word в HTML

## 🛡️ **Безопасность:**

- ✅ **Временные ссылки** - автоматическое истечение через 40 минут
- ✅ **HMAC подписи** - защита от подделки токенов
- ✅ **Валидация файлов** - проверка формата и размера
- ✅ **Админский доступ** - только для авторизованных пользователей
- ✅ **Rate limiting** - защита от атак

## 🐳 **Docker развертывание:**

```bash
# Продакшен
docker-compose -f docker-compose.prod.yml up -d

# Разработка
docker-compose up -d
```

## 📱 **Telegram Mini App:**

- **URL настройка:** `https://your-domain.com/miniapp`
- **Безопасный просмотр** PDF и Word файлов
- **Адаптивный интерфейс** для мобильных устройств
- **Навигация по страницам** для PDF файлов

## 🎯 **Готово к продакшену:**

- ✅ Полная документация
- ✅ Docker конфигурация
- ✅ Nginx настройки
- ✅ SSL поддержка
- ✅ Мониторинг и логирование
- ✅ Обработка ошибок
- ✅ Тестирование

## 📞 **Поддержка:**

Если у вас есть вопросы по настройке или использованию:
1. Изучите документацию в папке проекта
2. Проверьте примеры конфигурации в `.env.example`
3. Обратитесь к README файлам для конкретных функций

---

**🎉 Проект готов к использованию! Удачного развертывания!**