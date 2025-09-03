#!/usr/bin/env python3
"""
Простой SSL менеджер для Flask
"""

import os
import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta

class SimpleSSLManager:
    def __init__(self):
        self.ssl_dir = 'ssl'
        self.cert_file = os.path.join(self.ssl_dir, 'cert.pem')
        self.key_file = os.path.join(self.ssl_dir, 'key.pem')
    
    def is_ssl_ready(self):
        """Проверяет готовность SSL"""
        return (os.path.exists(self.cert_file) and 
                os.path.exists(self.key_file) and
                os.path.getsize(self.cert_file) > 0 and
                os.path.getsize(self.key_file) > 0)
    
    def get_ssl_context(self):
        """Возвращает SSL контекст для Flask"""
        if not self.is_ssl_ready():
            return None
        
        try:
            # Создаем SSL контекст
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(self.cert_file, self.key_file)
            return context
        except Exception as e:
            print(f"❌ Ошибка создания SSL контекста: {e}")
            return None
    
    def generate_self_signed(self):
        """Генерирует самоподписанный сертификат"""
        try:
            # Создаем папку если её нет
            if not os.path.exists(self.ssl_dir):
                os.makedirs(self.ssl_dir)
            
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
                x509.NameAttribute(x509.NameOID.COMMON_NAME, "localhost"),
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
                datetime.utcnow() + timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.IPAddress("127.0.0.1"),
                    x509.IPAddress("::1"),
                    x509.DNSName("localhost"),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256(), default_backend())
            
            # Сохраняем сертификат
            with open(self.cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            # Сохраняем приватный ключ
            with open(self.key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Устанавливаем права доступа
            os.chmod(self.cert_file, 0o644)
            os.chmod(self.key_file, 0o600)
            
            print(f"✅ Самоподписанный сертификат создан:")
            print(f"   Сертификат: {self.cert_file}")
            print(f"   Ключ: {self.key_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка генерации сертификата: {e}")
            return False
    
    def save_certificate(self, cert_text, key_text):
        """Сохраняет сертификат и ключ из текста"""
        try:
            # Создаем папку если её нет
            if not os.path.exists(self.ssl_dir):
                os.makedirs(self.ssl_dir)
            
            # Сохраняем сертификат
            with open(self.cert_file, 'w', encoding='utf-8') as f:
                f.write(cert_text)
            
            # Сохраняем ключ
            with open(self.key_file, 'w', encoding='utf-8') as f:
                f.write(key_text)
            
            # Устанавливаем права доступа
            os.chmod(self.cert_file, 0o644)
            os.chmod(self.key_file, 0o600)
            
            print(f"✅ SSL файлы сохранены:")
            print(f"   Сертификат: {self.cert_file}")
            print(f"   Ключ: {self.key_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка сохранения SSL файлов: {e}")
            return False

# Глобальный экземпляр
ssl_manager = SimpleSSLManager()