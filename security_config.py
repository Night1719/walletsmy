#!/usr/bin/env python3
"""
Конфигурация безопасности для BG Survey Platform
"""

import os
import secrets
from datetime import timedelta

class SecurityConfig:
    """Класс для настройки безопасности приложения"""
    
    @staticmethod
    def get_security_config():
        """Возвращает конфигурацию безопасности"""
        return {
            # Основные настройки безопасности
            'SECRET_KEY': os.environ.get('SECRET_KEY', secrets.token_hex(32)),
            'WTF_CSRF_ENABLED': True,
            'WTF_CSRF_TIME_LIMIT': 3600,  # 1 час
            
            # Настройки сессий
            'PERMANENT_SESSION_LIFETIME': timedelta(hours=2),
            'SESSION_COOKIE_SECURE': True,  # Только HTTPS
            'SESSION_COOKIE_HTTPONLY': True,  # Защита от XSS
            'SESSION_COOKIE_SAMESITE': 'Lax',  # CSRF защита
            
            # Настройки базы данных
            'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL', 'sqlite:///surveys.db'),
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'connect_args': {'check_same_thread': False} if 'sqlite' in os.environ.get('DATABASE_URL', '') else {}
            },
            
            # Настройки для продакшена
            'DEBUG': False,
            'TESTING': False,
            
            # Лимиты запросов
            'RATELIMIT_STORAGE_URL': 'memory://',
            'RATELIMIT_DEFAULT': '1000 per hour',
            
            # Настройки файлов
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB максимум
            'UPLOAD_FOLDER': 'uploads',
            'ALLOWED_EXTENSIONS': {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'xls'},
        }
    
    @staticmethod
    def get_security_headers():
        """Возвращает HTTP заголовки безопасности"""
        return {
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' cdnjs.cloudflare.com fonts.googleapis.com; "
                "font-src 'self' cdnjs.cloudflare.com fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            ),
            'Permissions-Policy': (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "speaker=(), "
                "vibrate=(), "
                "fullscreen=(self), "
                "payment=()"
            )
        }
    
    @staticmethod
    def get_rate_limits():
        """Возвращает лимиты для различных эндпоинтов"""
        return {
            'login': '20 per minute',
            'register': '3 per minute',
            'create_survey': '10 per hour',
            'submit_survey': '20 per hour',
            'export_excel': '5 per hour',
            'admin_panel': '100 per hour',
            'api': '100 per hour',
            'default': '1000 per hour'
        }
    
    @staticmethod
    def validate_input(data, field_type='text', max_length=1000):
        """Валидация входных данных"""
        if not data:
            return None
            
        # Удаляем потенциально опасные символы
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\r', '\n']
        for char in dangerous_chars:
            data = data.replace(char, '')
        
        # Ограничиваем длину
        if len(data) > max_length:
            data = data[:max_length]
        
        # Специальная валидация для разных типов
        if field_type == 'email':
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data):
                return None
        
        elif field_type == 'username':
            import re
            username_pattern = r'^[a-zA-Z0-9_-]{3,20}$'
            if not re.match(username_pattern, data):
                return None
        
        elif field_type == 'url':
            import re
            url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            if not re.match(url_pattern, data):
                return None
        
        return data.strip()
    
    @staticmethod
    def sanitize_html(text):
        """Очистка HTML от потенциально опасных тегов"""
        import re
        
        # Разрешенные теги
        allowed_tags = ['b', 'i', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li']
        
        # Удаляем все теги кроме разрешенных
        pattern = r'<(?!\/?(?:' + '|'.join(allowed_tags) + ')\b)[^>]*>'
        text = re.sub(pattern, '', text)
        
        # Удаляем атрибуты из тегов
        text = re.sub(r'<(\w+)[^>]*>', r'<\1>', text)
        
        return text
    
    @staticmethod
    def check_ip_whitelist(ip_address):
        """Проверка IP адреса по whitelist (если настроен)"""
        whitelist = os.environ.get('IP_WHITELIST', '').split(',')
        if whitelist and whitelist[0]:  # Если whitelist настроен
            return ip_address in whitelist
        return True  # Если whitelist не настроен, разрешаем все
    
    @staticmethod
    def log_security_event(event_type, details, ip_address=None):
        """Логирование событий безопасности"""
        import logging
        
        logger = logging.getLogger('security')
        logger.setLevel(logging.INFO)
        
        # Создаем обработчик для файла логов
        if not logger.handlers:
            handler = logging.FileHandler('security.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        log_message = f"{event_type}: {details}"
        if ip_address:
            log_message += f" (IP: {ip_address})"
        
        logger.warning(log_message)