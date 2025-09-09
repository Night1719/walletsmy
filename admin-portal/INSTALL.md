# Установка и настройка Админского Портала

## Быстрый старт

### 1. Клонирование и переход в директорию
```bash
git clone <repository-url>
cd admin-portal
```

### 2. Запуск через Docker (рекомендуется)
```bash
./start.sh
```

### 3. Доступ к приложению
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Документация**: http://localhost:8000/docs

## Ручная установка

### Требования
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Backend установка
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend установка
```bash
cd frontend
npm install
npm run dev
```

## Добавление ваших скриптов

### 1. Структура директорий
```
scripts/
├── monitoring/     # Скрипты мониторинга
├── backup/         # Скрипты резервного копирования
└── maintenance/    # Скрипты обслуживания
```

### 2. Требования к скриптам
- Исполняемые права: `chmod +x script.py`
- Возврат кода выхода:
  - `0` - успех
  - `1` - предупреждение
  - `2` - критическая ошибка
  - `3` - системная ошибка

### 3. Загрузка через веб-интерфейс
1. Откройте http://localhost:3000/scripts
2. Нажмите "Загрузить скрипт"
3. Выберите файл и категорию
4. Добавьте описание

### 4. Загрузка через API
```bash
curl -X POST "http://localhost:8000/api/scripts/upload" \
  -F "file=@your_script.py" \
  -F "category=monitoring" \
  -F "description=My monitoring script"
```

## Настройка мониторинга

### 1. Метрики системы
- CPU использование
- Память (RAM)
- Дисковое пространство
- Сетевая активность

### 2. Пороговые значения
- CPU > 80% - предупреждение
- CPU > 90% - критическое
- Память > 85% - предупреждение
- Память > 95% - критическое
- Диск > 90% - критическое

### 3. Настройка алертов
Алерты настраиваются в файле `backend/services/metrics_service.py`

## Уведомления

### Типы уведомлений
- **info** - информационные
- **warning** - предупреждения
- **error** - ошибки
- **success** - успешные операции

### Уровни важности
- **low** - низкий
- **medium** - средний
- **high** - высокий
- **critical** - критический

## API Документация

Полная документация API доступна по адресу:
http://localhost:8000/docs

### Основные endpoints:
- `GET /api/metrics/system` - текущие метрики
- `GET /api/scripts` - список скриптов
- `POST /api/scripts/upload` - загрузка скрипта
- `POST /api/scripts/{id}/execute` - выполнение скрипта
- `GET /api/logs` - просмотр логов
- `GET /api/notifications` - уведомления

## Troubleshooting

### Проблемы с Docker
```bash
# Очистка контейнеров
docker-compose down -v
docker system prune -f

# Пересборка
docker-compose up --build
```

### Проблемы с правами на скрипты
```bash
chmod +x scripts/*/*.py
```

### Проблемы с базой данных
```bash
# Сброс базы данных
docker-compose down -v
docker-compose up -d postgres
```

## Разработка

### Структура проекта
```
admin-portal/
├── backend/           # FastAPI приложение
│   ├── api/          # API endpoints
│   ├── models/       # Модели данных
│   ├── services/     # Бизнес-логика
│   └── utils/        # Утилиты
├── frontend/         # Next.js приложение
│   ├── src/          # Исходный код
│   └── components/   # React компоненты
├── scripts/          # Пользовательские скрипты
└── logs/             # Логи системы
```

### Добавление новых функций
1. Backend: добавьте endpoint в `api/`
2. Frontend: создайте компонент в `components/`
3. Обновите навигацию в `Sidebar.tsx`

## Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs -f`
2. Проверьте статус сервисов: `docker-compose ps`
3. Создайте issue в репозитории