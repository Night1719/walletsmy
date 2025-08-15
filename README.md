# BG Surveys

Корпоративная платформа для создания и прохождения опросов (Banter Group).

Возможности:
- Авторизация по логину/паролю (сессии)
- Роли: admin, creator, analyst, user
- Админ-панель: создание/редактирование пользователей, импорт из LDAP
- Создание опросов, редактор вопросов (через JSON), шеринговые ссылки
- Прохождение опросов: анонимно (с записью внутреннего IP) и с авторизацией
- Аналитика результатов (диаграммы по вариантам, счетчики текстовых ответов)
- Темная/светлая тема, фирменные цвета BG
- Установка на отдельный VPS без облачных сервисов

## Быстрый старт (локально)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Затем откройте `http://127.0.0.1:8000/login`.

## Установка на Ubuntu 24.04 (VPS)

Скрипт настроит PostgreSQL, Python venv, Systemd-сервис и Nginx.

```bash
sudo -i
cd /opt
# Скопируйте/разверните репозиторий в /opt/bg-surveys или используйте /workspace как источник
# Если вы в среде с данным кодом, просто:
chmod +x /workspace/install.sh
/workspace/install.sh
```
Скрипт спросит:
- Домен или IP, публичный URL
- Данные администратора
- Параметры БД
- Параметры LDAP (опционально)

После установки:
- Приложение: systemd сервис `bg-surveys` (порт 8085 за Nginx)
- Конфиг окружения: `/opt/bg-surveys/.env`
- Логи: `journalctl -u bg-surveys -f`

## Роли и доступ
- admin: полный доступ, админка, управление ролями и пользователями
- creator: создание и редактирование своих опросов, аналитика своих
- analyst: просмотр аналитики (там где назначено; в этой версии – все активные)
- user: прохождение опросов

## Редактор опросов
В редакторе указывается JSON с массивом вопросов:
```json
[
  {"text":"Ваше мнение о BG?", "qtype":"text"},
  {"text":"Как оцените сервис?","qtype":"single","options":["Отлично","Хорошо","Удовл.","Плохо"]},
  {"text":"Какие функции используете?","qtype":"multiple","options":["А","Б","В"]}
]
```
`qtype`: `text` | `single` | `multiple`.

## Анонимные и авторизованные опросы
- Если опрос анонимный, ответы не связываются с пользователем. В запрос сохраняется внутренний IP (из `X-Forwarded-For`/`X-Real-IP`).
- Если опрос не анонимный, требуется вход.

## LDAP импорт
В админке укажите Base DN, фильтр и атрибуты. Настройки подключения берутся из `.env`:
```
LDAP_SERVER_URI=ldap://host:389
LDAP_BIND_DN=cn=admin,dc=example,dc=com
LDAP_BIND_PASSWORD=secret
LDAP_BASE_DN=dc=example,dc=com
```

## Бэкапы
- БД PostgreSQL: `pg_dump bg_surveys > backup.sql`
- Приложение: каталог `/opt/bg-surveys/`

## Обновление
```bash
sudo systemctl stop bg-surveys
# Обновить код в /opt/bg-surveys (git pull / rsync)
sudo -u www-data /opt/bg-surveys/venv/bin/pip install -r /opt/bg-surveys/requirements.txt
sudo systemctl start bg-surveys
```

## Лицензия
Внутреннее корпоративное приложение BG.