#!/usr/bin/env python3
"""
Interactive Certificate Installation Script
"""
import os
import sys
from pathlib import Path
import tempfile

def main():
    print("🔐 Интерактивная установка SSL сертификата")
    print("=" * 50)
    
    # Create certificates directory
    cert_dir = Path(__file__).parent / "certificates"
    cert_dir.mkdir(exist_ok=True)
    
    print("\n📋 Введите ваш SSL сертификат:")
    print("   (Включая -----BEGIN CERTIFICATE----- и -----END CERTIFICATE-----)")
    print("   (Введите 'END' на новой строке когда закончите)")
    print()
    
    cert_lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == 'END':
                break
            cert_lines.append(line)
        except KeyboardInterrupt:
            print("\n❌ Отменено пользователем")
            return 1
        except EOFError:
            break
    
    cert_text = '\n'.join(cert_lines)
    
    if not cert_text.strip():
        print("❌ Сертификат не введен")
        return 1
    
    # Validate certificate format
    if '-----BEGIN CERTIFICATE-----' not in cert_text:
        print("❌ Неверный формат сертификата")
        print("   Убедитесь, что сертификат включает -----BEGIN CERTIFICATE-----")
        return 1
    
    if '-----END CERTIFICATE-----' not in cert_text:
        print("❌ Неверный формат сертификата")
        print("   Убедитесь, что сертификат включает -----END CERTIFICATE-----")
        return 1
    
    # Save certificate
    cert_file = cert_dir / "server.crt"
    with open(cert_file, 'w', encoding='utf-8') as f:
        f.write(cert_text)
    
    print(f"✅ Сертификат сохранен: {cert_file}")
    
    # Ask for private key
    print("\n🔑 Введите приватный ключ (опционально):")
    print("   (Включая -----BEGIN PRIVATE KEY----- и -----END PRIVATE KEY-----)")
    print("   (Введите 'SKIP' чтобы пропустить)")
    print()
    
    key_lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == 'SKIP':
                break
            if line.strip().upper() == 'END':
                break
            key_lines.append(line)
        except KeyboardInterrupt:
            print("\n⏭️  Пропуск приватного ключа")
            break
        except EOFError:
            break
    
    key_text = '\n'.join(key_lines) if key_lines else None
    key_file = None
    
    if key_text and '-----BEGIN' in key_text:
        key_file = cert_dir / "server.key"
        with open(key_file, 'w', encoding='utf-8') as f:
            f.write(key_text)
        print(f"✅ Приватный ключ сохранен: {key_file}")
    else:
        print("⏭️  Приватный ключ пропущен")
    
    # Ask for password
    password = None
    if key_file:
        print("\n🔐 Введите пароль для сертификата (опционально):")
        try:
            password = input().strip() or None
        except KeyboardInterrupt:
            password = None
        except EOFError:
            password = None
    
    # Update .env file
    env_file = Path(__file__).parent / ".env"
    
    # Read current .env
    env_lines = []
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            env_lines = f.readlines()
    
    # Update SSL configuration
    ssl_config = {
        'SSL_VERIFY': 'true',
        'SSL_VERIFY_CERT': 'true',
        'SSL_VERIFY_HOSTNAME': 'true',
        'SSL_CERT_PATH': str(cert_file),
    }
    
    if key_file:
        ssl_config['SSL_KEY_PATH'] = str(key_file)
    
    if password:
        ssl_config['SSL_PASSWORD'] = password
    
    # Update .env content
    updated_lines = []
    ssl_section_found = False
    
    for line in env_lines:
        if line.startswith('# === SSL Configuration ==='):
            ssl_section_found = True
            updated_lines.append(line)
            # Add SSL config
            for key, value in ssl_config.items():
                updated_lines.append(f"{key}={value}\n")
        elif line.startswith('SSL_'):
            # Skip old SSL lines
            continue
        else:
            updated_lines.append(line)
    
    # If SSL section not found, add it
    if not ssl_section_found:
        updated_lines.append('\n# === SSL Configuration ===\n')
        for key, value in ssl_config.items():
            updated_lines.append(f"{key}={value}\n")
    
    # Write updated .env
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    print(f"✅ .env файл обновлен: {env_file}")
    
    # Test configuration
    print("\n🧪 Проверка конфигурации...")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from config import SSL_CERT_PATH, SSL_VERIFY
        print(f"✅ SSL_CERT_PATH: {SSL_CERT_PATH}")
        print(f"✅ SSL_VERIFY: {SSL_VERIFY}")
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return 1
    
    print("\n🎉 Установка сертификата завершена!")
    print("\n📁 Созданные файлы:")
    print(f"   {cert_file}")
    if key_file:
        print(f"   {key_file}")
    
    print("\n🚀 Теперь можно запускать Mini App:")
    print("   python run.py")
    print("   или")
    print("   run_ssl.bat")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())