#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска BG Survey Platform в продакшене
Использует Gunicorn WSGI сервер для высокой производительности
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_dependencies():
    """Проверка необходимых зависимостей"""
    try:
        import gunicorn
        print("✅ Gunicorn найден")
    except ImportError:
        print("❌ Gunicorn не установлен")
        print("Установите: pip install gunicorn")
        return False
    
    try:
        import flask
        print("✅ Flask найден")
    except ImportError:
        print("❌ Flask не установлен")
        print("Установите: pip install flask")
        return False
    
    return True

def create_gunicorn_config():
    """Создание конфигурации Gunicorn"""
    config_content = """# Gunicorn конфигурация для BG Survey Platform
import multiprocessing

# Количество рабочих процессов
workers = multiprocessing.cpu_count() * 2 + 1

# Тип рабочих процессов
worker_class = 'sync'

# Время ожидания для рабочих процессов
timeout = 120

# Максимальное количество запросов на рабочий процесс
max_requests = 1000
max_requests_jitter = 100

# Перезапуск рабочих процессов
preload_app = True

# Логирование
accesslog = 'logs/gunicorn_access.log'
errorlog = 'logs/gunicorn_error.log'
loglevel = 'info'

# Биндинг
bind = '0.0.0.0:8000'

# Пользователь и группа (для Linux)
# user = 'www-data'
# group = 'www-data'

# PID файл
pidfile = 'gunicorn.pid'

# Переменные окружения
raw_env = [
    'FLASK_CONFIG=production',
]
"""
    
    config_path = Path('gunicorn.conf.py')
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✅ Конфигурация Gunicorn создана: {config_path}")
    return config_path

def create_systemd_service():
    """Создание systemd сервиса для Linux"""
    service_content = """[Unit]
Description=BG Survey Platform
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/bg-survey-platform
Environment=PATH=/path/to/bg-survey-platform/venv/bin
ExecStart=/path/to/bg-survey-platform/venv/bin/gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
"""
    
    service_path = Path('bg-survey-platform.service')
    with open(service_path, 'w', encoding='utf-8') as f:
        f.write(service_content)
    
    print(f"✅ Systemd сервис создан: {service_path}")
    print("⚠️  Не забудьте изменить пути в файле сервиса!")
    return service_path

def create_nginx_config():
    """Создание конфигурации Nginx"""
    nginx_config = """server {
    listen 80;
    server_name your-domain.com;
    
    # Редирект на HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL сертификаты
    ssl_certificate /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;
    
    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Статические файлы
    location /static/ {
        alias /path/to/bg-survey-platform/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Проксирование к Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
    
    # Безопасность
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
"""
    
    nginx_path = Path('nginx.conf')
    with open(nginx_path, 'w', encoding='utf-8') as f:
        f.write(nginx_config)
    
    print(f"✅ Конфигурация Nginx создана: {nginx_path}")
    print("⚠️  Не забудьте изменить домен и пути в конфигурации!")
    return nginx_path

def run_gunicorn(host='0.0.0.0', port=8000, workers=None, config_file=None):
    """Запуск Gunicorn сервера"""
    
    if not check_dependencies():
        return False
    
    # Создаем директорию для логов
    Path('logs').mkdir(exist_ok=True)
    
    # Базовые параметры
    cmd = ['gunicorn']
    
    if config_file and Path(config_file).exists():
        cmd.extend(['-c', config_file])
    else:
        # Параметры командной строки
        cmd.extend([
            '--bind', f'{host}:{port}',
            '--workers', str(workers or 4),
            '--worker-class', 'sync',
            '--timeout', '120',
            '--access-logfile', 'logs/gunicorn_access.log',
            '--error-logfile', 'logs/gunicorn_error.log',
            '--log-level', 'info',
            '--preload'
        ])
    
    cmd.append('app:app')
    
    print(f"🚀 Запуск Gunicorn с параметрами: {' '.join(cmd)}")
    print(f"📱 Приложение будет доступно по адресу: http://{host}:{port}")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print()
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Сервер остановлен пользователем")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка запуска Gunicorn: {e}")
        return False
    
    return True

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description='BG Survey Platform - Запуск в продакшене')
    parser.add_argument('--host', default='0.0.0.0', help='Хост для биндинга (по умолчанию: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='Порт для биндинга (по умолчанию: 8000)')
    parser.add_argument('--workers', type=int, default=4, help='Количество рабочих процессов (по умолчанию: 4)')
    parser.add_argument('--config', help='Путь к конфигурационному файлу Gunicorn')
    parser.add_argument('--create-config', action='store_true', help='Создать конфигурационные файлы')
    parser.add_argument('--create-service', action='store_true', help='Создать systemd сервис')
    parser.add_argument('--create-nginx', action='store_true', help='Создать конфигурацию Nginx')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("BG Survey Platform - Запуск в продакшене")
    print("=" * 60)
    print()
    
    # Создание конфигурационных файлов
    if args.create_config:
        create_gunicorn_config()
        print()
    
    if args.create_service:
        create_systemd_service()
        print()
    
    if args.create_nginx:
        create_nginx_config()
        print()
    
    # Запуск сервера
    if not args.create_config and not args.create_service and not args.create_nginx:
        success = run_gunicorn(
            host=args.host,
            port=args.port,
            workers=args.workers,
            config_file=args.config
        )
        
        if not success:
            sys.exit(1)
    else:
        print("✅ Конфигурационные файлы созданы")
        print("📖 Прочитайте README.md для инструкций по настройке")

if __name__ == '__main__':
    main()