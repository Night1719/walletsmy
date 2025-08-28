# 🎯 BG Опросник - Система опросов для Бантер Групп

## 📁 О проекте
Полнофункциональная система для создания и проведения опросов, разработанная специально для Бантер Групп.

## 🚀 Быстрый запуск

### Windows:
```cmd
run_windows.bat
```

### Linux/Mac:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations users
python manage.py makemigrations surveys
python manage.py migrate
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None; user = User.objects.get(username='admin'); user.role = 'admin'; user.can_create_surveys = True; user.save()"
python manage.py collectstatic --noinput
python manage.py runserver 127.0.0.1:8000
```

## 🔑 Доступ
- **Сайт**: http://127.0.0.1:8000
- **Админка**: http://127.0.0.1:8000/admin
- **Логин**: admin
- **Пароль**: admin123

## 📋 Возможности

### ✅ Авторизация
- Логин/пароль (не Google)
- Роли пользователей (admin, moderator, user)
- Управление доступом к созданию опросов

### ✅ Админ панель
- Создание и управление пользователями
- Импорт пользователей из LDAP
- Управление опросами и результатами

### ✅ Опросы
- Создание опросов с различными типами вопросов
- Анонимные опросы (с отслеживанием IP)
- Опросы с авторизацией
- Публичные ссылки для прохождения

### ✅ Дизайн
- Темная и светлая тема
- Корпоративные цвета Бантер Групп
- Адаптивный интерфейс для всех устройств

### ✅ Аналитика
- Просмотр результатов опросов
- Экспорт данных в CSV
- Статистика и графики

## 🏗️ Структура проекта
```
bg_survey_system/
├── manage.py              ← Django управление
├── run_windows.bat        ← Windows скрипт запуска
├── requirements.txt       ← Зависимости Python
├── bg_survey/             ← Настройки Django
├── users/                 ← Пользователи и авторизация
├── surveys/               ← Система опросов
├── templates/             ← HTML шаблоны
└── static/                ← CSS, JS, изображения
```

## 🎨 Дизайн
- **Корпоративные цвета**: красный, серый, белый, черный
- **Bootstrap 5**: современный и адаптивный интерфейс
- **Иконки**: Bootstrap Icons для лучшего UX
- **Темы**: поддержка светлой и темной темы

## 🔧 Технологии
- **Backend**: Django 5.2.5
- **Frontend**: Bootstrap 5.3, HTML5, CSS3
- **База данных**: SQLite (для разработки)
- **LDAP**: интеграция с корпоративными серверами
- **Формы**: Django Forms + Crispy Forms

## 📱 Адаптивность
- Мобильные устройства
- Планшеты
- Десктопы
- Все современные браузеры

## 🚨 Особенности
- **Чистый код**: без лишних файлов от других проектов
- **Простой запуск**: один скрипт для Windows
- **Полная функциональность**: все необходимые возможности
- **Готовность к продакшену**: можно развертывать на сервере

## 🎯 Готово к использованию!
Проект полностью настроен и готов к запуску.

**Используйте `run_windows.bat` для автоматического запуска! 🚀**