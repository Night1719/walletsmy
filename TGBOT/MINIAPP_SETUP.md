# Telegram Mini App для просмотра инструкций

## Обзор

Telegram Mini App позволяет пользователям просматривать инструкции (PDF и Word документы) прямо в Telegram без необходимости скачивания файлов.

## 🚀 Возможности

### Просмотр файлов
- **PDF файлы**: Полноценный просмотр с навигацией по страницам
- **Word документы**: Отображение с возможностью скачивания
- **Адаптивный интерфейс**: Оптимизирован для мобильных устройств

### Функции интерфейса
- Навигация по страницам PDF
- Масштабирование (zoom in/out)
- Скачивание файлов
- Темная/светлая тема (автоматически по настройкам Telegram)

## 🏗️ Архитектура

### Компоненты
- **Flask приложение** (`app.py`) - основной сервер
- **HTML шаблоны** - пользовательский интерфейс
- **PDF.js** - просмотр PDF файлов
- **Nginx** - обратный прокси и SSL терминация

### Маршруты
- `/` - главная страница с выбором инструкций
- `/viewer/<type>/<format>` - просмотр конкретного файла
- `/api/instructions/<type>` - API для получения списка файлов
- `/api/file/<type>/<format>` - API для скачивания файлов
- `/api/convert/<type>/<format>` - API для конвертации файлов

## ⚙️ Установка и настройка

### 1. Установка зависимостей

```bash
cd miniapp
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```env
# Telegram Bot Token
TELEGRAM_BOT_TOKEN=your_bot_token_here

# File Server Configuration
FILE_SERVER_BASE_URL=https://files.example.com
FILE_SERVER_USER=your_file_server_user
FILE_SERVER_PASS=your_file_server_password
FILE_SERVER_USE_AUTH=true

# Mini App Configuration
MINIAPP_URL=https://your-domain.com/miniapp
FLASK_SECRET_KEY=your_secret_key_here

# Server Configuration
MINIAPP_HOST=0.0.0.0
MINIAPP_PORT=5000
MINIAPP_DEBUG=false
```

### 3. Запуск приложения

```bash
# Разработка
python run.py

# Продакшен
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 4. Docker развертывание

```bash
# Сборка образа
docker build -t helpdesk-miniapp .

# Запуск контейнера
docker run -d \
  --name helpdesk-miniapp \
  -p 5000:5000 \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e FILE_SERVER_BASE_URL=https://files.example.com \
  helpdesk-miniapp
```

### 5. Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f miniapp
```

## 🔧 Конфигурация

### Nginx конфигурация

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL сертификаты
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # Mini App
    location /miniapp {
        proxy_pass http://miniapp:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API
    location /api/ {
        proxy_pass http://miniapp:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL сертификаты

```bash
# Генерация самоподписанного сертификата (для тестирования)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Или использование Let's Encrypt
certbot --nginx -d your-domain.com
```

## 📱 Интеграция с ботом

### Обновление обработчика инструкций

Бот теперь отправляет кнопку Mini App вместо файлов:

```python
# Создание кнопки Mini App
web_app_info = WebAppInfo(url=MINIAPP_URL)
kb = InlineKeyboardBuilder()
kb.button(text="📚 Открыть инструкции", web_app=web_app_info)

# Отправка сообщения с кнопкой
await message.answer(
    "📚 Инструкции: iPhone\n\n"
    "📄 Доступные форматы: PDF, DOCX\n\n"
    "✅ Нажмите кнопку ниже для просмотра инструкций в удобном интерфейсе",
    reply_markup=kb.as_markup()
)
```

## 🔐 Безопасность

### Валидация Telegram данных

```python
def _validate_telegram_data(init_data: str, bot_token: str) -> bool:
    """Validate Telegram Mini App init data"""
    # Проверка подписи данных от Telegram
    # Предотвращает поддельные запросы
```

### Ограничения доступа

- Проверка подписи Telegram WebApp данных
- Валидация типов инструкций
- Ограничение размера файлов
- Rate limiting через Nginx

## 📊 Мониторинг

### Логирование

```python
# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s'
)
```

### Метрики

- Количество просмотров файлов
- Время загрузки файлов
- Ошибки конвертации
- Активность пользователей

## 🧪 Тестирование

### Локальное тестирование

```bash
# Запуск в режиме разработки
export MINIAPP_DEBUG=true
python run.py

# Тестирование API
curl http://localhost:5000/api/instructions/1c_ar2
```

### Тестирование в Telegram

1. Настройте webhook для бота
2. Отправьте команду `/start` в бот
3. Перейдите в раздел "Инструкции"
4. Выберите тип инструкции
5. Нажмите кнопку "Открыть инструкции"

## 🔧 Устранение неполадок

### Частые проблемы

1. **"Unauthorized" ошибка**
   - Проверьте `TELEGRAM_BOT_TOKEN`
   - Убедитесь, что Mini App настроен в BotFather

2. **Файлы не загружаются**
   - Проверьте `FILE_SERVER_BASE_URL`
   - Убедитесь в правильности аутентификации

3. **PDF не отображается**
   - Проверьте, что PDF.js загружается
   - Убедитесь в корректности base64 данных

### Отладка

```bash
# Просмотр логов
docker-compose logs -f miniapp

# Проверка конфигурации
python -c "from config import *; print(f'MiniApp URL: {MINIAPP_URL}')"

# Тестирование API
curl -v http://localhost:5000/api/instructions/1c_ar2
```

## 📈 Производительность

### Оптимизации

- Кэширование файлов на уровне Nginx
- Сжатие gzip для статических файлов
- Оптимизация PDF.js
- Асинхронная загрузка файлов

### Масштабирование

- Горизонтальное масштабирование через Docker Swarm
- Load balancing через Nginx
- Кэширование через Redis (опционально)

## ✅ Итог

Telegram Mini App предоставляет:

- ✅ **Удобный просмотр** PDF и Word файлов
- ✅ **Интеграция с Telegram** через WebApp API
- ✅ **Безопасность** через валидацию данных
- ✅ **Адаптивный дизайн** для мобильных устройств
- ✅ **Простое развертывание** через Docker
- ✅ **Масштабируемость** для больших нагрузок

Система готова к использованию в продакшене!