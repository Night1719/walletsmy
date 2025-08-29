#!/usr/bin/env python3
"""
SSL Manager для BG Survey Platform
Управление SSL сертификатами и настройками
"""

import os
import ssl
import socket
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend

class SSLManager:
    """Менеджер SSL сертификатов"""
    
    def __init__(self, ssl_dir='ssl'):
        self.ssl_dir = ssl_dir
        self.cert_file = os.path.join(ssl_dir, 'cert.pem')
        self.key_file = os.path.join(ssl_dir, 'key.pem')
        self.chain_file = os.path.join(ssl_dir, 'chain.pem')
        
        # Создаем папку SSL если её нет
        if not os.path.exists(ssl_dir):
            os.makedirs(ssl_dir)
    
    def get_ssl_status(self):
        """Получает текущий статус SSL"""
        status = {
            'enabled': False,
            'certificate': None,
            'error': None
        }
        
        try:
            # Проверяем наличие файлов
            if os.path.exists(self.cert_file) and os.path.exists(self.key_file):
                status['enabled'] = True
                
                # Парсим сертификат
                cert_info = self._parse_certificate()
                if cert_info:
                    status['certificate'] = cert_info
                else:
                    status['error'] = 'Ошибка парсинга сертификата'
                    
        except Exception as e:
            status['error'] = str(e)
        
        return status
    
    def _parse_certificate(self):
        """Парсит информацию о сертификате"""
        try:
            with open(self.cert_file, 'rb') as f:
                cert_data = f.read()
            
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            
            return {
                'subject': str(cert.subject),
                'issuer': str(cert.issuer),
                'not_before': cert.not_valid_before.strftime('%Y-%m-%d'),
                'not_after': cert.not_valid_after.strftime('%Y-%m-%d'),
                'serial_number': str(cert.serial_number),
                'version': cert.version
            }
        except Exception as e:
            print(f"Ошибка парсинга сертификата: {e}")
            return None
    
    def validate_certificate(self):
        """Проверяет валидность сертификата"""
        try:
            if not os.path.exists(self.cert_file) or not os.path.exists(self.key_file):
                return False, "Файлы сертификата или ключа не найдены"
            
            # Проверяем права доступа к ключу
            key_stat = os.stat(self.key_file)
            if key_stat.st_mode & 0o777 != 0o600:
                return False, "Небезопасные права доступа к приватному ключу"
            
            # Проверяем синтаксис сертификата
            cert_info = self._parse_certificate()
            if not cert_info:
                return False, "Неверный формат сертификата"
            
            # Проверяем срок действия
            cert = x509.load_pem_x509_certificate(
                open(self.cert_file, 'rb').read(), 
                default_backend()
            )
            
            now = datetime.now()
            if now < cert.not_valid_before or now > cert.not_valid_after:
                return False, "Сертификат недействителен по времени"
            
            return True, "Сертификат валиден"
            
        except Exception as e:
            return False, f"Ошибка валидации: {str(e)}"
    
    def test_ssl_connection(self, host='localhost', port=443):
        """Тестирует SSL соединение"""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((host, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    return True, f"SSL соединение установлено. Сертификат: {cert.get('subject', 'Unknown')}"
                    
        except Exception as e:
            return False, f"Ошибка SSL соединения: {str(e)}"
    
    def generate_self_signed(self, common_name='localhost', days=365):
        """Генерирует самоподписанный сертификат"""
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
            
            # Генерируем приватный ключ
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Создаем сертификат
            subject = issuer = x509.Name([
                x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "RU"),
                x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, "Moscow"),
                x509.NameAttribute(x509.NameOID.LOCALITY_NAME, "Moscow"),
                x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "BunterGroup"),
                x509.NameAttribute(x509.NameOID.COMMON_NAME, common_name),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow().replace(year=datetime.utcnow().year + 1)
            ).sign(private_key, hashes.SHA256(), default_backend())
            
            # Сохраняем файлы
            with open(self.key_file, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=Encoding.PEM,
                    format=PrivateFormat.PKCS8,
                    encryption_algorithm=NoEncryption()
                ))
            
            with open(self.cert_file, 'wb') as f:
                f.write(cert.public_bytes(Encoding.PEM))
            
            # Устанавливаем правильные права доступа
            os.chmod(self.key_file, 0o600)
            os.chmod(self.cert_file, 0o644)
            
            return True, "Самоподписанный сертификат создан успешно"
            
        except Exception as e:
            return False, f"Ошибка генерации сертификата: {str(e)}"
    
    def get_ssl_config(self):
        """Возвращает конфигурацию SSL для Flask"""
        if not self.is_ssl_ready():
            return None
        
        return {
            'ssl_context': (
                self.cert_file,
                self.key_file
            )
        }
    
    def is_ssl_ready(self):
        """Проверяет готовность SSL к использованию"""
        try:
            is_valid, _ = self.validate_certificate()
            return is_valid
        except:
            return False

# Глобальный экземпляр менеджера
ssl_manager = SSLManager()

def get_ssl_status():
    """Получает статус SSL для админ панели"""
    return ssl_manager.get_ssl_status()

def is_ssl_enabled():
    """Проверяет, включен ли SSL"""
    return ssl_manager.is_ssl_ready()

def get_ssl_config():
    """Получает конфигурацию SSL для Flask"""
    return ssl_manager.get_ssl_config()