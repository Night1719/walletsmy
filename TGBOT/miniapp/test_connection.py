#!/usr/bin/env python3
"""
Test Mini App connection
"""
import requests
import ssl
import socket

def test_connection():
    """Test connection to Mini App"""
    url = "https://127.0.0.1:4477"
    
    print("🧪 Тестирование подключения к Mini App")
    print("=" * 40)
    
    # Test 1: Socket connection
    print("1. Тест сокетного подключения...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(("127.0.0.1", 4477))
        sock.close()
        
        if result == 0:
            print("✅ Сокетное подключение успешно")
        else:
            print(f"❌ Сокетное подключение failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Ошибка сокетного подключения: {e}")
        return False
    
    # Test 2: HTTP request
    print("\n2. Тест HTTP запроса...")
    try:
        response = requests.get(url, verify=False, timeout=5)
        print(f"✅ HTTP запрос успешен: {response.status_code}")
    except requests.exceptions.SSLError as e:
        print(f"⚠️  SSL ошибка (ожидаемо): {e}")
        print("   Это нормально для самоподписного сертификата")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка HTTP запроса: {e}")
        return False
    
    # Test 3: Mini App endpoint
    print("\n3. Тест Mini App endpoint...")
    try:
        response = requests.get(f"{url}/miniapp", verify=False, timeout=5)
        print(f"✅ Mini App endpoint доступен: {response.status_code}")
    except Exception as e:
        print(f"❌ Mini App endpoint недоступен: {e}")
        return False
    
    print("\n🎉 Все тесты пройдены!")
    print(f"🌐 Mini App доступен по адресу: {url}")
    return True

if __name__ == "__main__":
    test_connection()