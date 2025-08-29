import os
from datetime import timedelta

class Config:
    """Базовая конфигурация приложения"""
    
    # Основные настройки
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    APP_NAME = 'BG Survey Platform'
    APP_VERSION = '1.0.0'
    COMPANY_NAME = 'BunterGroup'
    
    # База данных
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///surveys.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки сессии
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Настройки безопасности
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Настройки загрузки файлов
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    
    # Настройки LDAP (для будущей интеграции)
    LDAP_SERVER = os.environ.get('LDAP_SERVER') or 'ldap://localhost:389'
    LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN') or 'dc=example,dc=com'
    LDAP_USER_DN = os.environ.get('LDAP_USER_DN') or 'cn=admin,dc=example,dc=com'
    LDAP_PASSWORD = os.environ.get('LDAP_PASSWORD') or ''
    LDAP_USER_SEARCH_BASE = os.environ.get('LDAP_USER_SEARCH_BASE') or 'ou=users,dc=example,dc=com'
    
    # Настройки почты (для будущих уведомлений)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or ''
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
    
    # Настройки логирования
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'app.log'
    
    # Настройки производительности
    SQLALCHEMY_POOL_SIZE = int(os.environ.get('SQLALCHEMY_POOL_SIZE') or 10)
    SQLALCHEMY_MAX_OVERFLOW = int(os.environ.get('SQLALCHEMY_MAX_OVERFLOW') or 20)
    SQLALCHEMY_POOL_TIMEOUT = int(os.environ.get('SQLALCHEMY_POOL_TIMEOUT') or 30)
    
    # Настройки SSL (для продакшена)
    SSL_CONTEXT = os.environ.get('SSL_CONTEXT') or None
    
    @staticmethod
    def init_app(app):
        """Инициализация конфигурации для приложения"""
        pass

class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    
    DEBUG = True
    SQLALCHEMY_ECHO = True
    
    # Настройки для разработки
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0

class TestingConfig(Config):
    """Конфигурация для тестирования"""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    
    DEBUG = False
    
    # Безопасность для продакшена
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # SSL настройки
    SSL_CONTEXT = 'adhoc'  # Автоматическая генерация SSL сертификата
    
    @classmethod
    def init_app(cls, app):
        """Инициализация для продакшена"""
        Config.init_app(app)
        
        # Логирование в файл
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            file_handler = RotatingFileHandler(
                'logs/bg_survey_platform.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('BG Survey Platform startup')

class DockerConfig(ProductionConfig):
    """Конфигурация для Docker"""
    
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        
        # Логирование в stdout для Docker
        import logging
        logging.basicConfig(level=logging.INFO)

# Словарь конфигураций
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Получение конфигурации из переменной окружения"""
    config_name = os.environ.get('FLASK_CONFIG') or 'default'
    return config[config_name]