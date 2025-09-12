# Telegram Bot с Mini App для инструкций

Telegram бот с Mini App для просмотра инструкций в различных форматах.

## Запуск

### 1. Настройка .env файла
Скопируйте `.env.example` в `.env` и заполните:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_USER_IDS=your_user_id_here
```

### 2. Установка зависимостей для Mini App
```cmd
cd miniapp
pip install -r requirements.txt
```

### 3. Запуск Mini App
```cmd
python run.py
```

### 4. Запуск бота
```cmd
python bot.py
```

## Возможности

- 📚 **Раздел "Инструкции"** с категориями и подкатегориями
- 🔐 **OTP аутентификация** по email для доступа к инструкциям
- 📄 **Просмотр файлов** - PDF, Word, видео, текст
- 🔒 **Безопасные ссылки** с истечением срока действия (40 минут)
- 👨‍💼 **Админ панель** для управления инструкциями
- 📱 **Mini App** для просмотра файлов в Telegram

## Структура

```
TGBOT/
├── bot.py                    # Основной файл бота
├── config.py                 # Конфигурация
├── handlers/                 # Обработчики команд
├── keyboards.py              # Клавиатуры
├── states.py                 # FSM состояния
├── instruction_manager.py    # Управление инструкциями
├── miniapp/                  # Mini App
│   ├── app.py               # Flask приложение
│   ├── run.py               # Скрипт запуска
│   └── templates/           # HTML шаблоны
└── instructions/            # Папка с инструкциями
```

## Настройка

Все настройки в `.env` файле. По умолчанию:
- Mini App: `http://localhost:4477`
- SSL: отключен
- Режим: local