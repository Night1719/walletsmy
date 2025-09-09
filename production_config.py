#!/usr/bin/env python3
"""
Конфигурация для продакшена BG Survey Platform
"""

import os
from security_config import SecurityConfig

class ProductionConfig:
    """Конфигурация для продакшена"""
    
    @staticmethod
    def get_production_config():
        """Возвращает конфигурацию для продакшена"""
        base_config = SecurityConfig.get_security_config()
        
        # Переопределяем настройки для продакшена
        production_config = {
            **base_config,
            
            # Основные настройки
            'DEBUG': False,
            'TESTING': False,
            
            # Безопасность
            'SECRET_KEY': os.environ.get('SECRET_KEY', os.urandom(32).hex()),
            'WTF_CSRF_ENABLED': True,
            'WTF_CSRF_TIME_LIMIT': 3600,
            
            # Сессии
            'PERMANENT_SESSION_LIFETIME': 7200,  # 2 часа
            'SESSION_COOKIE_SECURE': True,
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Lax',
            
            # База данных
            'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost/surveys'),
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'pool_size': 10,
                'max_overflow': 20,
                'pool_timeout': 30,
            },
            
            # Логирование
            'LOG_LEVEL': 'WARNING',
            'LOG_FILE': 'app.log',
            
            # Лимиты
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
            'RATELIMIT_STORAGE_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
            
            # SSL/TLS
            'SSL_REDIRECT': True,
            'FORCE_HTTPS': True,
        }
        
        return production_config
    
    @staticmethod
    def setup_logging():
        """Настройка логирования для продакшена"""
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Настройка основного логгера
        logging.basicConfig(
            level=logging.WARNING,
            format='%(asctime)s %(levelname)s %(name)s %(message)s'
        )
        
        # Логгер для безопасности
        security_logger = logging.getLogger('security')
        security_handler = RotatingFileHandler(
            'security.log', maxBytes=10*1024*1024, backupCount=5
        )
        security_handler.setLevel(logging.WARNING)
        security_formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        security_handler.setFormatter(security_formatter)
        security_logger.addHandler(security_handler)
        
        # Логгер для приложения
        app_logger = logging.getLogger('app')
        app_handler = RotatingFileHandler(
            'app.log', maxBytes=10*1024*1024, backupCount=5
        )
        app_handler.setLevel(logging.WARNING)
        app_formatter = logging.Formatter(
            '%(asctime)s - APP - %(levelname)s - %(message)s'
        )
        app_handler.setFormatter(app_formatter)
        app_logger.addHandler(app_handler)
    
    @staticmethod
    def setup_monitoring():
        """Настройка мониторинга"""
        try:
            import psutil
            
            # Мониторинг ресурсов
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Логируем критические значения
            if cpu_percent > 80:
                logging.warning(f"High CPU usage: {cpu_percent}%")
            
            if memory.percent > 80:
                logging.warning(f"High memory usage: {memory.percent}%")
            
            if disk.percent > 90:
                logging.warning(f"High disk usage: {disk.percent}%")
                
        except ImportError:
            pass  # psutil не установлен
    
    @staticmethod
    def get_nginx_config():
        """Возвращает конфигурацию Nginx для продакшена"""
        return """
# Nginx конфигурация для BG Survey Platform

upstream survey_app {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL сертификаты
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Заголовки безопасности
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Ограничения
    client_max_body_size 16M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
    
    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://survey_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /login {
        limit_req zone=login burst=3 nodelay;
        proxy_pass http://survey_app;
    }
    
    # Статические файлы
    location /static {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
"""
    
    @staticmethod
    def get_docker_compose():
        """Возвращает Docker Compose конфигурацию"""
        return """
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://survey_user:${DB_PASSWORD}@db:5432/survey_db
      - SECRET_KEY=${SECRET_KEY}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped
    
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=survey_db
      - POSTGRES_USER=survey_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
"""