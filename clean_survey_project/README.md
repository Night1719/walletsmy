# 🎯 BG Опросник - Чистая версия

## 📁 О проекте
Это **ЧИСТАЯ** версия системы опросов для Бантер Групп, без лишних файлов от других проектов.

## 🚀 Быстрый запуск

### Windows:
```cmd
run_clean_opros.bat
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
- ✅ Авторизация пользователей
- ✅ Админ панель
- ✅ Создание и управление опросами
- ✅ Анонимные и авторизованные опросы
- ✅ LDAP интеграция
- ✅ Красивый дизайн с корпоративными цветами
- ✅ Аналитика результатов

## 🎨 Дизайн
- Темная/светлая тема
- Корпоративные цвета Бантер Групп (красный, серый, белый, черный)
- Адаптивный интерфейс

## 🏗️ Структура
```
clean_survey_project/
├── manage.py              ← Django управление
├── run_clean_opros.bat    ← Windows скрипт
├── requirements.txt       ← Зависимости
├── survey_project/        ← Настройки Django
├── users/                 ← Пользователи
├── surveys/               ← Опросы
├── templates/             ← HTML шаблоны
└── static/                ← CSS, JS, изображения
```

## 🎯 Готово к использованию!
Проект полностью настроен и готов к запуску.