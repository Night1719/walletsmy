# 🚀 Быстрый запуск BG Survey Platform

## 📋 Требования

- **Python 3.8+** (рекомендуется 3.11)
- **pip** (менеджер пакетов Python)
- **Git** (для клонирования репозитория)

## 🖥️ Windows

### Автоматический запуск (рекомендуется)

1. **Скачайте и запустите** `run_windows.bat`
2. **Дождитесь** автоматической установки
3. **Откройте браузер** и перейдите по адресу: http://localhost:5000

### Ручной запуск

```cmd
# Клонирование репозитория
git clone <repository-url>
cd bg-survey-platform

# Создание виртуального окружения
python -m venv venv
venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения
python app.py
```

## 🐧 Linux / macOS

### Автоматический запуск (рекомендуется)

```bash
# Сделать скрипт исполняемым
chmod +x run_linux.sh

# Запустить
./run_linux.sh
```

### Ручной запуск

```bash
# Клонирование репозитория
git clone <repository-url>
cd bg-survey-platform

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения
python app.py
```

## 🐳 Docker

### Быстрый запуск с Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f bg-survey-platform

# Остановка
docker-compose down
```

### Запуск только приложения

```bash
# Сборка образа
docker build -t bg-survey-platform .

# Запуск контейнера
docker run -p 8000:8000 bg-survey-platform
```

## 🔑 Первый вход

После запуска приложения:

1. **Откройте браузер** и перейдите по адресу: http://localhost:5000
2. **Нажмите "Войти в систему"**
3. **Используйте учетные данные по умолчанию:**
   - **Администратор**: `admin` / `admin123`
   - **Тестовый пользователь**: `test_user` / `test123`
   - **Обычный пользователь**: `user` / `user123`

## ⚠️ Важно!

- **Измените пароли по умолчанию** в продакшене
- **Настройте переменные окружения** для продакшена
- **Используйте HTTPS** в продакшене
- **Регулярно создавайте резервные копии** базы данных

## 🛠️ Дополнительные инструменты

### Создание администратора

```bash
python create_admin.py
```

### Инициализация базы данных

```bash
python init_db.py
```

### Запуск в продакшене

```bash
python run_production.py --create-config
```

## 📱 Доступ к приложению

- **Главная страница**: http://localhost:5000
- **Панель управления**: http://localhost:5000/dashboard
- **Админ панель**: http://localhost:5000/admin
- **Создание опроса**: http://localhost:5000/surveys/create

## 🔧 Настройка

### Переменные окружения

Создайте файл `.env` в корневой директории:

```env
FLASK_CONFIG=development
SECRET_KEY=your-super-secret-key
DATABASE_URL=sqlite:///surveys.db
```

### Конфигурация для продакшена

```bash
# Создание конфигурационных файлов
python run_production.py --create-config --create-service --create-nginx

# Запуск с Gunicorn
python run_production.py --host 0.0.0.0 --port 8000 --workers 4
```

## 🆘 Решение проблем

### Ошибка "Port already in use"

```bash
# Найти процесс, использующий порт 5000
lsof -i :5000  # Linux/macOS
netstat -ano | findstr :5000  # Windows

# Остановить процесс
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows
```

### Ошибка "Module not found"

```bash
# Активировать виртуальное окружение
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Переустановить зависимости
pip install -r requirements.txt
```

### Ошибка "Permission denied"

```bash
# Исправить права на директории
chmod 755 logs uploads  # Linux/macOS
```

## 📞 Поддержка

Если у вас возникли проблемы:

1. **Проверьте логи** в директории `logs/`
2. **Убедитесь**, что все зависимости установлены
3. **Проверьте версию Python** (должна быть 3.8+)
4. **Создайте issue** в репозитории проекта

## 🎯 Что дальше?

После успешного запуска:

1. **Изучите интерфейс** - создайте тестовый опрос
2. **Настройте пользователей** - создайте учетные записи для команды
3. **Настройте права доступа** - определите, кто может создавать опросы
4. **Создайте первый опрос** - протестируйте функциональность
5. **Настройте для продакшена** - используйте Gunicorn и Nginx

---

**Удачного использования BG Survey Platform! 🎉**