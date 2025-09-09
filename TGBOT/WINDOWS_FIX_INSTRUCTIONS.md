# 🔧 Исправление ошибок для Windows

## ❌ Проблемы, которые были исправлены:

1. **Отсутствующая переменная `SCREENSHOT_KEYWORDS`** в `config.py`
2. **Неправильное использование состояний FSM** в `handlers/admin.py`
3. **Отсутствующие импорты** `State` и `StatesGroup`

## ✅ Решение:

### **Шаг 1: Замените файл `config.py`**

Замените содержимое файла `config.py` на исправленную версию из `config_windows_fixed.py`

### **Шаг 2: Создайте файл `.env`**

Создайте файл `.env` в папке `TGBOT` с содержимым из `.env_windows_example`:

```env
# === Основные настройки ===
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_USER_IDS=your_telegram_id

# === Mini App (для локального тестирования) ===
MINIAPP_URL=http://localhost:5000/miniapp
MINIAPP_WEBHOOK_URL=http://localhost:5000
MINIAPP_MODE=local
LINK_EXPIRY_MINUTES=40

# === File Restrictions ===
ALLOWED_FILE_EXTENSIONS=pdf,docx,doc,txt
FORBIDDEN_FILE_EXTENSIONS=png,jpg,jpeg,gif,bmp,tiff,webp,ico,svg,psd,ai,sketch
MAX_FILE_SIZE_MB=50
ENABLE_CONTENT_VALIDATION=true
SCREENSHOT_KEYWORDS=screenshot,screen,shot,скриншот,скрин,снимок
```

### **Шаг 3: Установите зависимости**

```cmd
pip install -r requirements.txt
```

### **Шаг 4: Запустите бота**

```cmd
python bot.py
```

## 🎯 Минимальная конфигурация для тестирования:

Если вы хотите только протестировать бота без Mini App, используйте:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_USER_IDS=your_telegram_id
MINIAPP_MODE=local
```

## 🚀 Запуск Mini App (опционально):

Если хотите протестировать Mini App:

1. **Установите зависимости Mini App:**
   ```cmd
   cd miniapp
   pip install -r requirements.txt
   ```

2. **Запустите Mini App:**
   ```cmd
   python run.py
   ```

3. **В другом терминале запустите бота:**
   ```cmd
   python bot.py
   ```

## ✅ Проверка исправления:

После исправления бот должен запуститься без ошибок и показать:

```
Bot started successfully!
```

## 🔍 Если все еще есть ошибки:

1. Убедитесь, что все файлы исправлены
2. Проверьте, что файл `.env` создан правильно
3. Убедитесь, что все зависимости установлены
4. Проверьте, что `TELEGRAM_BOT_TOKEN` и `ADMIN_USER_IDS` заполнены

## 📞 Поддержка:

Если проблемы остаются, проверьте:
- Версию Python (должна быть 3.8+)
- Установленные пакеты
- Правильность токена бота
- Правильность ID администратора