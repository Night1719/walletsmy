#!/usr/bin/env python3
"""
Скрипт для генерации SSL сертификата
"""

from simple_ssl import ssl_manager

def main():
    print("🔒 Генерация SSL сертификата для BG Survey Platform")
    print("=" * 50)
    
    if ssl_manager.is_ssl_ready():
        print("✅ SSL сертификат уже существует!")
        print(f"   Сертификат: {ssl_manager.cert_file}")
        print(f"   Ключ: {ssl_manager.key_file}")
        
        choice = input("\nХотите пересоздать? (y/N): ").lower()
        if choice != 'y':
            print("❌ Отменено")
            return
    else:
        print("📝 SSL сертификат не найден")
    
    print("\n🔄 Генерация самоподписанного сертификата...")
    
    if ssl_manager.generate_self_signed():
        print("\n✅ SSL сертификат успешно создан!")
        print("🚀 Теперь запустите сервер:")
        print("   python3 app.py")
        print("\n🌐 Сервер должен запуститься с HTTPS на порту 5000")
    else:
        print("\n❌ Ошибка создания SSL сертификата")

if __name__ == '__main__':
    main()