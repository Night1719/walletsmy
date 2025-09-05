#!/usr/bin/env python3
"""
Middleware для безопасности BG Survey Platform
"""

import time
import hashlib
from functools import wraps
from flask import request, jsonify, g, abort
from collections import defaultdict, deque
import re

class SecurityMiddleware:
    """Middleware для обеспечения безопасности"""
    
    def __init__(self, app=None):
        self.app = app
        self.rate_limits = defaultdict(lambda: deque())
        self.failed_attempts = defaultdict(int)
        self.blocked_ips = set()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Инициализация middleware"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Регистрируем обработчики ошибок
        app.register_error_handler(429, self.rate_limit_handler)
        app.register_error_handler(403, self.forbidden_handler)
        app.register_error_handler(400, self.bad_request_handler)
    
    def before_request(self):
        """Обработка запроса перед выполнением"""
        # Получаем IP адрес
        ip_address = self.get_client_ip()
        g.client_ip = ip_address
        
        # Проверяем заблокированные IP
        if ip_address in self.blocked_ips:
            abort(403)
        
        # Проверяем rate limiting
        if not self.check_rate_limit(ip_address, request.endpoint):
            abort(429)
        
        # Проверяем подозрительную активность
        if self.detect_suspicious_activity(request):
            self.log_security_event('SUSPICIOUS_ACTIVITY', 
                                  f"Endpoint: {request.endpoint}, Method: {request.method}",
                                  ip_address)
            abort(400)
        
        # Валидируем входные данные
        self.validate_request_data()
    
    def after_request(self, response):
        """Обработка ответа после выполнения"""
        # Добавляем заголовки безопасности
        from security_config import SecurityConfig
        security_headers = SecurityConfig.get_security_headers()
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        # Логируем подозрительные ответы
        if response.status_code >= 400:
            self.log_security_event('HTTP_ERROR', 
                                  f"Status: {response.status_code}, Path: {request.path}",
                                  g.get('client_ip'))
        
        return response
    
    def get_client_ip(self):
        """Получение реального IP адреса клиента"""
        # Проверяем заголовки прокси
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def check_rate_limit(self, ip_address, endpoint):
        """Проверка лимитов запросов"""
        from security_config import SecurityConfig
        
        # Получаем лимит для эндпоинта
        rate_limits = SecurityConfig.get_rate_limits()
        limit = rate_limits.get(endpoint, rate_limits['default'])
        
        # Парсим лимит (например, "100 per hour")
        try:
            count, period = limit.split(' per ')
            count = int(count)
            
            # Определяем время в секундах
            period_seconds = {
                'minute': 60,
                'hour': 3600,
                'day': 86400
            }.get(period, 3600)
            
            current_time = time.time()
            
            # Очищаем старые записи
            while (self.rate_limits[ip_address] and 
                   self.rate_limits[ip_address][0] < current_time - period_seconds):
                self.rate_limits[ip_address].popleft()
            
            # Проверяем лимит
            if len(self.rate_limits[ip_address]) >= count:
                return False
            
            # Добавляем текущий запрос
            self.rate_limits[ip_address].append(current_time)
            return True
            
        except (ValueError, KeyError):
            return True  # Если не можем распарсить, разрешаем
    
    def detect_suspicious_activity(self, request):
        """Обнаружение подозрительной активности"""
        # Проверяем на SQL инъекции
        sql_patterns = [
            r'union\s+select', r'drop\s+table', r'delete\s+from',
            r'insert\s+into', r'update\s+set', r'exec\s*\(',
            r'script\s*>', r'<script', r'javascript:',
            r'<iframe', r'<object', r'<embed'
        ]
        
        # Проверяем все параметры запроса
        for key, value in request.values.items():
            if isinstance(value, str):
                for pattern in sql_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        return True
        
        # Проверяем размер запроса
        if request.content_length and request.content_length > 16 * 1024 * 1024:  # 16MB
            return True
        
        # Проверяем на слишком частые запросы
        ip_address = self.get_client_ip()
        if len(self.rate_limits[ip_address]) > 50:  # Более 50 запросов в минуту
            return True
        
        return False
    
    def validate_request_data(self):
        """Валидация данных запроса"""
        from security_config import SecurityConfig
        
        # Валидируем JSON данные
        if request.is_json:
            try:
                data = request.get_json()
                self.validate_json_data(data)
            except Exception:
                abort(400)
        
        # Валидируем form данные
        for key, value in request.form.items():
            if isinstance(value, str):
                validated_value = SecurityConfig.validate_input(value)
                if validated_value is None:
                    abort(400)
    
    def validate_json_data(self, data, max_depth=10, current_depth=0):
        """Рекурсивная валидация JSON данных"""
        if current_depth > max_depth:
            raise ValueError("JSON too deep")
        
        if isinstance(data, dict):
            for key, value in data.items():
                if not isinstance(key, str) or len(key) > 100:
                    raise ValueError("Invalid key")
                self.validate_json_data(value, max_depth, current_depth + 1)
        elif isinstance(data, list):
            if len(data) > 1000:  # Максимум 1000 элементов
                raise ValueError("List too long")
            for item in data:
                self.validate_json_data(item, max_depth, current_depth + 1)
        elif isinstance(data, str):
            if len(data) > 10000:  # Максимум 10KB строки
                raise ValueError("String too long")
    
    def log_security_event(self, event_type, details, ip_address=None):
        """Логирование событий безопасности"""
        import logging
        
        logger = logging.getLogger('security')
        logger.setLevel(logging.WARNING)
        
        if not logger.handlers:
            handler = logging.FileHandler('security.log')
            formatter = logging.Formatter(
                '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        log_message = f"{event_type}: {details}"
        if ip_address:
            log_message += f" (IP: {ip_address})"
        
        logger.warning(log_message)
    
    def rate_limit_handler(self, error):
        """Обработчик ошибки rate limit"""
        return jsonify({
            'error': 'Too Many Requests',
            'message': 'Превышен лимит запросов. Попробуйте позже.',
            'retry_after': 60
        }), 429
    
    def forbidden_handler(self, error):
        """Обработчик ошибки 403"""
        return jsonify({
            'error': 'Forbidden',
            'message': 'Доступ запрещен'
        }), 403
    
    def bad_request_handler(self, error):
        """Обработчик ошибки 400"""
        return jsonify({
            'error': 'Bad Request',
            'message': 'Некорректный запрос'
        }), 400

def require_security_headers(f):
    """Декоратор для принудительного добавления заголовков безопасности"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        # Добавляем дополнительные заголовки для критических эндпоинтов
        if hasattr(response, 'headers'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        return response
    return decorated_function

def admin_only(f):
    """Декоратор для доступа только администраторам"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(limit='100 per hour'):
    """Декоратор для ограничения скорости запросов"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import g
            from security_middleware import SecurityMiddleware
            
            middleware = SecurityMiddleware()
            if not middleware.check_rate_limit(g.get('client_ip'), f.__name__):
                abort(429)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator