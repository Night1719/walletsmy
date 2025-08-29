#!/usr/bin/env python3
"""
Скрипт для исправления прав доступа к SSL файлам
"""

import os
import stat

def fix_ssl_permissions():
    """Исправляет права доступа к SSL файлам"""
    
    ssl_dir = 'ssl'
    
    if not os.path.exists(ssl_dir):
        print(f"❌ Папка {ssl_dir} не найдена")
        return False
    
    cert_path = os.path.join(ssl_dir, 'cert.pem')
    key_path = os.path.join(ssl_dir, 'key.pem')
    
    print("🔧 Исправление прав доступа к SSL файлам...")
    
    # Исправляем права для сертификата (644 - владелец читает/пишет, группа и другие читают)
    if os.path.exists(cert_path):
        os.chmod(cert_path, 0o644)
        current_perms = oct(os.stat(cert_path).st_mode)[-3:]
        print(f"✅ Сертификат: {current_perms} (должно быть 644)")
    else:
        print(f"❌ Файл сертификата не найден: {cert_path}")
    
    # Исправляем права для ключа (600 - только владелец читает/пишет)
    if os.path.exists(key_path):
        os.chmod(key_path, 0o600)
        current_perms = oct(os.stat(key_path).st_mode)[-3:]
        print(f"✅ Ключ: {current_perms} (должно быть 600)")
    else:
        print(f"❌ Файл ключа не найден: {key_path}")
    
    # Проверяем содержимое файлов
    print("\n📋 Проверка содержимого файлов:")
    
    if os.path.exists(cert_path):
        try:
            with open(cert_path, 'r') as f:
                content = f.read()
                if '-----BEGIN CERTIFICATE-----' in content and '-----END CERTIFICATE-----' in content:
                    print(f"✅ Сертификат: валидный формат, размер {len(content)} символов")
                else:
                    print(f"❌ Сертификат: неверный формат")
        except Exception as e:
            print(f"❌ Ошибка чтения сертификата: {e}")
    
    if os.path.exists(key_path):
        try:
            with open(key_path, 'r') as f:
                content = f.read()
                if ('-----BEGIN PRIVATE KEY-----' in content or '-----BEGIN RSA PRIVATE KEY-----' in content) and '-----END PRIVATE KEY-----' in content:
                    print(f"✅ Ключ: валидный формат, размер {len(content)} символов")
                else:
                    print(f"❌ Ключ: неверный формат")
        except Exception as e:
            print(f"❌ Ошибка чтения ключа: {e}")
    
    return True

if __name__ == '__main__':
    fix_ssl_permissions()