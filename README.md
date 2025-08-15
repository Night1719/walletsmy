# BG Surveys

Корпоративная платформа для создания и прохождения опросов (Banter Group).

Возможности:
- Авторизация по логину/паролю (сессии)
- Роли: admin, creator, analyst, user
- Админ-панель: создание/редактирование пользователей, импорт из LDAP
- Создание опросов, визуальный редактор вопросов, шеринговые ссылки
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

### Встроенный администратор при первом запуске
Если в БД нет пользователей, на старте автоматически создается администратор:
- Логин: `Admin`
- Пароль: `R2b9rfo8`
После входа обязательно смените пароль!

## Установка на Ubuntu 24.04 (VPS)

Скрипт настроит PostgreSQL, Python venv, Systemd-сервис и Nginx.

```bash
sudo -i
cd /opt
chmod +x /workspace/install.sh
/workspace/install.sh
```
Скрипт спросит:
- Домен или IP, публичный URL
- Данные администратора (можно сразу задать свои)
- Параметры БД
- Параметры LDAP (опционально)

После установки:
- Приложение: systemd сервис `bg-surveys` (порт 8085 за Nginx)
- Конфиг окружения: `/opt/bg-surveys/.env`
- Логи: `journalctl -u bg-surveys -f`

## Роли и доступ
- admin: полный доступ, админка, управление ролями и пользователями
- creator: создание и редактирование своих опросов, аналитика своих
- analyst: просмотр аналитики
- user: прохождение опросов

## TLS/HTTPS для Nginx
Есть два варианта.

### Вариант A: Готовые сертификаты (корпоративный CA)
1) Скопируйте файлы в:
- Сертификат: `/etc/ssl/certs/bg_surveys.crt`
- Ключ: `/etc/ssl/private/bg_surveys.key`

2) Обновите конфиг Nginx `/etc/nginx/sites-available/bg-surveys`:
```nginx
server {
	listen 80;
	server_name YOUR_DOMAIN;
	return 301 https://$host$request_uri;
}

server {
	listen 443 ssl http2;
	server_name YOUR_DOMAIN;

	ssl_certificate /etc/ssl/certs/bg_surveys.crt;
	ssl_certificate_key /etc/ssl/private/bg_surveys.key;
	ssl_protocols TLSv1.2 TLSv1.3;
	ssl_ciphers HIGH:!aNULL:!MD5;

	client_max_body_size 20m;

	location /static/ {
		alias /opt/bg-surveys/app/static/;
	}
	location / {
		proxy_pass http://127.0.0.1:8085;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
	}
}
```
3) Проверка и перезапуск:
```bash
nginx -t && systemctl reload nginx
```

### Вариант B: Let’s Encrypt (Certbot)
1) Установите certbot:
```bash
apt-get update && apt-get install -y certbot python3-certbot-nginx
```
2) Выпустите сертификат и настройте Nginx автоматически:
```bash
certbot --nginx -d YOUR_DOMAIN --redirect --agree-tos -m admin@YOUR_DOMAIN --non-interactive
```
3) Проверка автообновления:
```bash
systemctl status certbot.timer
```

## Редактор опросов
В редакторе можно визуально добавлять вопросы и варианты, менять порядок и типы (text/single/multiple). Всё сохраняется как JSON в скрытом поле формы и отправляется на сервер.

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
sudo -u www-data /opt/bg-surveys/venv/bin/pip install -r /opt/bg-surveys/requirements.txt
sudo systemctl start bg-surveys
```

## Лицензия
Внутреннее корпоративное приложение BG.