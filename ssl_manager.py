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
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(common_name),
                    x509.IPAddress("127.0.0.1"),
                    x509.IPAddress("::1")
                ]),
                critical=False
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
    
    def setup_lets_encrypt(self, domain, email):
        """Настраивает Let's Encrypt сертификат"""
        try:
            import subprocess
            import tempfile
            
            # Проверяем наличие certbot
            try:
                subprocess.run(['certbot', '--version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False, "Certbot не установлен. Установите: sudo apt install certbot"
            
            # Создаем временный конфиг для certbot
            config_content = f"""
[webroot]
webroot-path = /tmp/letsencrypt
webroot-root = /tmp/letsencrypt
domains = {domain}
email = {email}
agree-tos = True
non-interactive = True
"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
                f.write(config_content)
                config_file = f.name
            
            try:
                # Создаем временную папку для веб-рута
                os.makedirs('/tmp/letsencrypt', exist_ok=True)
                
                # Запускаем certbot
                result = subprocess.run([
                    'certbot', 'certonly',
                    '--config', config_file,
                    '--webroot',
                    '--webroot-path', '/tmp/letsencrypt'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Копируем сертификаты
                    cert_source = f'/etc/letsencrypt/live/{domain}/fullchain.pem'
                    key_source = f'/etc/letsencrypt/live/{domain}/privkey.pem'
                    
                    if os.path.exists(cert_source) and os.path.exists(key_source):
                        # Копируем с sudo правами
                        subprocess.run(['sudo', 'cp', cert_source, self.cert_file], check=True)
                        subprocess.run(['sudo', 'cp', key_source, self.key_file], check=True)
                        
                        # Устанавливаем права доступа
                        subprocess.run(['sudo', 'chown', f'{os.getuid()}:{os.getgid()}', self.cert_file], check=True)
                        subprocess.run(['sudo', 'chown', f'{os.getuid()}:{os.getgid()}', self.key_file], check=True)
                        os.chmod(self.key_file, 0o600)
                        os.chmod(self.cert_file, 0o644)
                        
                        return True, f"Let's Encrypt сертификат для {domain} установлен успешно"
                    else:
                        return False, "Сертификаты не найдены после генерации"
                else:
                    return False, f"Ошибка certbot: {result.stderr}"
                    
            finally:
                # Очищаем временные файлы
                os.unlink(config_file)
                subprocess.run(['sudo', 'rm', '-rf', '/tmp/letsencrypt'], check=False)
                
        except Exception as e:
            return False, f"Ошибка настройки Let's Encrypt: {str(e)}"
    
    def validate_certificate_format(self):
        """Проверяет формат сертификата"""
        try:
            if not os.path.exists(self.cert_file):
                return False, "Файл сертификата не найден"
            
            # Проверяем что это PEM файл
            with open(self.cert_file, 'r') as f:
                content = f.read()
                if not content.startswith('-----BEGIN CERTIFICATE-----'):
                    return False, "Неверный формат сертификата (должен быть PEM)"
            
            # Проверяем что это приватный ключ
            if not os.path.exists(self.key_file):
                return False, "Файл приватного ключа не найден"
            
            with open(self.key_file, 'r') as f:
                content = f.read()
                if not content.startswith('-----BEGIN PRIVATE KEY-----') and not content.startswith('-----BEGIN RSA PRIVATE KEY-----'):
                    return False, "Неверный формат приватного ключа (должен быть PEM)"
            
            return True, "Формат файлов корректен"
            
        except Exception as e:
            return False, f"Ошибка проверки формата: {str(e)}"
    
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