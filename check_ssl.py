#!/usr/bin/env python3
"""
Скрипт проверки SSL сертификатов BG Survey Platform
Диагностика и настройка SSL
"""

import os
import sys

def check_ssl_files():
    """Проверяет наличие SSL файлов"""
    print("🔍 Проверка SSL файлов...")
    print("=" * 50)
    
    ssl_dir = "ssl"
    cert_file = os.path.join(ssl_dir, "cert.pem")
    key_file = os.path.join(ssl_dir, "key.pem")
    
    # Проверяем папку SSL
    if not os.path.exists(ssl_dir):
        print(f"❌ Папка {ssl_dir} не найдена")
        return False
    
    print(f"✅ Папка {ssl_dir} найдена")
    
    # Проверяем файлы
    files_status = {
        "cert.pem": os.path.exists(cert_file),
        "key.pem": os.path.exists(key_file)
    }
    
    for filename, exists in files_status.items():
        if exists:
            filepath = os.path.join(ssl_dir, filename)
            size = os.path.getsize(filepath)
            print(f"✅ {filename} - найден ({size} байт)")
        else:
            print(f"❌ {filename} - не найден")
    
    return all(files_status.values())

def check_ssl_permissions():
    """Проверяет права доступа к SSL файлам"""
    print("\n🔐 Проверка прав доступа...")
    print("=" * 50)
    
    ssl_dir = "ssl"
    key_file = os.path.join(ssl_dir, "key.pem")
    
    if not os.path.exists(key_file):
        print("❌ Файл ключа не найден")
        return False
    
    # Проверяем права доступа к ключу
    stat = os.stat(key_file)
    mode = stat.st_mode & 0o777
    
    print(f"Права доступа к key.pem: {oct(mode)}")
    
    if mode == 0o600:
        print("✅ Права доступа корректны (600)")
        return True
    else:
        print("❌ Небезопасные права доступа!")
        print("   Рекомендуется: 600 (только владелец)")
        return False

def check_ssl_manager():
    """Проверяет SSL менеджер"""
    print("\n🔧 Проверка SSL менеджера...")
    print("=" * 50)
    
    try:
        from ssl_manager import SSLManager, get_ssl_status
        
        print("✅ SSL менеджер импортирован успешно")
        
        # Создаем экземпляр менеджера
        manager = SSLManager()
        print("✅ SSL менеджер создан")
        
        # Получаем статус
        status = get_ssl_status()
        print(f"Статус SSL: {'Включен' if status['enabled'] else 'Отключен'}")
        
        if status['certificate']:
            cert = status['certificate']
            print(f"Сертификат: {cert.get('subject', 'Unknown')}")
            print(f"Действителен до: {cert.get('not_after', 'Unknown')}")
        
        if status['error']:
            print(f"Ошибка: {status['error']}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта SSL менеджера: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка SSL менеджера: {e}")
        return False

def check_dependencies():
    """Проверяет зависимости для SSL"""
    print("\n📦 Проверка зависимостей...")
    print("=" * 50)
    
    required_modules = [
        'cryptography',
        'OpenSSL',
        'ssl',
        'socket'
    ]
    
    all_available = True
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} - доступен")
        except ImportError:
            print(f"❌ {module} - не доступен")
            all_available = False
    
    return all_available

def generate_self_signed():
    """Генерирует самоподписанный сертификат"""
    print("\n🎫 Генерация самоподписанного сертификата...")
    print("=" * 50)
    
    try:
        from ssl_manager import SSLManager
        
        manager = SSLManager()
        success, message = manager.generate_self_signed()
        
        if success:
            print(f"✅ {message}")
            return True
        else:
            print(f"❌ {message}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        return False

def main():
    """Основная функция"""
    print("🔒 Проверка SSL для BG Survey Platform")
    print("=" * 60)
    
    # Проверяем зависимости
    deps_ok = check_dependencies()
    if not deps_ok:
        print("\n⚠️  Установите недостающие зависимости:")
        print("   pip install -r requirements.txt")
        return
    
    # Проверяем файлы
    files_ok = check_ssl_files()
    
    # Проверяем права доступа
    if files_ok:
        permissions_ok = check_ssl_permissions()
        
        # Исправляем права доступа если нужно
        if not permissions_ok:
            print("\n🔧 Исправление прав доступа...")
            key_file = os.path.join("ssl", "key.pem")
            try:
                os.chmod(key_file, 0o600)
                print("✅ Права доступа исправлены")
                permissions_ok = True
            except Exception as e:
                print(f"❌ Не удалось исправить права: {e}")
    
    # Проверяем SSL менеджер
    manager_ok = check_ssl_manager()
    
    # Генерируем сертификат если нужно
    if not files_ok:
        print("\n🎫 Создание самоподписанного сертификата...")
        if generate_self_signed():
            print("✅ Сертификат создан! Перезапустите приложение.")
        else:
            print("❌ Не удалось создать сертификат")
    
    # Итоговая рекомендация
    print("\n" + "=" * 60)
    if files_ok and manager_ok:
        print("🎉 SSL готов к использованию!")
        print("   Перезапустите приложение для активации SSL")
    else:
        print("⚠️  SSL требует настройки")
        print("   Проверьте файлы и зависимости")

if __name__ == "__main__":
    main()