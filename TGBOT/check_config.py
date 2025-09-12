#!/usr/bin/env python3
"""
Check bot configuration
"""
from config import MINIAPP_URL, MINIAPP_MODE, SSL_VERIFY, SSL_VERIFY_CERT

print("🔍 Проверка конфигурации бота")
print("=" * 40)
print(f"MINIAPP_URL: {MINIAPP_URL}")
print(f"MINIAPP_MODE: {MINIAPP_MODE}")
print(f"SSL_VERIFY: {SSL_VERIFY}")
print(f"SSL_VERIFY_CERT: {SSL_VERIFY_CERT}")

# Check if URL is localhost
if "localhost" in MINIAPP_URL or "127.0.0.1" in MINIAPP_URL:
    print("✅ URL настроен для локального Mini App")
else:
    print("⚠️  URL указывает на внешний сервер")

# Check if HTTP
if MINIAPP_URL.startswith("http://"):
    print("✅ Используется HTTP (без SSL)")
elif MINIAPP_URL.startswith("https://"):
    print("⚠️  Используется HTTPS (требует SSL сертификат)")

print("\n💡 Если видите ошибки SSL:")
print("   1. Убедитесь, что Mini App запущен на localhost:4477")
print("   2. Проверьте, что в .env файле MINIAPP_URL=http://localhost:4477/miniapp")
print("   3. Перезапустите бота после изменения .env")