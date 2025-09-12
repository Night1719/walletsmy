#!/usr/bin/env python3
"""
Check .env file loading
"""
import os
from pathlib import Path
from dotenv import load_dotenv

print("🔍 Проверка загрузки .env файла")
print("=" * 40)

# Check current directory .env
current_env = Path(__file__).parent / ".env"
print(f"1. Текущая директория .env: {current_env}")
print(f"   Существует: {current_env.exists()}")

if current_env.exists():
    load_dotenv(current_env)
    print("   ✅ Загружен")

# Check parent directory .env
parent_env = Path(__file__).parent.parent / ".env"
print(f"\n2. Родительская директория .env: {parent_env}")
print(f"   Существует: {parent_env.exists()}")

if parent_env.exists():
    load_dotenv(parent_env)
    print("   ✅ Загружен")

# Check environment variables
print(f"\n3. Переменные окружения:")
print(f"   SSL_CERT_PATH: {os.getenv('SSL_CERT_PATH', 'НЕ НАЙДЕНА')}")
print(f"   SSL_KEY_PATH: {os.getenv('SSL_KEY_PATH', 'НЕ НАЙДЕНА')}")
print(f"   FLASK_HOST: {os.getenv('FLASK_HOST', 'НЕ НАЙДЕНА')}")
print(f"   FLASK_PORT: {os.getenv('FLASK_PORT', 'НЕ НАЙДЕНА')}")

# Check certificate files
cert_path = os.getenv('SSL_CERT_PATH', '')
key_path = os.getenv('SSL_KEY_PATH', '')

if cert_path and key_path:
    print(f"\n4. Файлы сертификата:")
    print(f"   Сертификат: {cert_path} - {'существует' if os.path.exists(cert_path) else 'НЕ НАЙДЕН'}")
    print(f"   Ключ: {key_path} - {'существует' if os.path.exists(key_path) else 'НЕ НАЙДЕН'}")
else:
    print(f"\n4. Пути к сертификату не настроены")

print(f"\n💡 Для настройки сертификата:")
print(f"   1. Создайте папку: mkdir certificates")
print(f"   2. Поместите файлы: bot.bunter.ru.crt и bot.bunter.ru.key")
print(f"   3. Перезапустите: python run.py")