"""
Run script for Telegram Mini App
"""
import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Also load from parent directory
parent_env = Path(__file__).parent.parent / ".env"
if parent_env.exists():
    load_dotenv(parent_env)

# Import and run the app
from app import app
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG

if __name__ == '__main__':
    print("🚀 Запуск Telegram Mini App...")
    print(f"📍 Хост: {FLASK_HOST}")
    print(f"🔌 Порт: {FLASK_PORT}")
    print(f"🐛 Режим отладки: {FLASK_DEBUG}")
    print(f"🌐 URL: https://bot.bunter.ru:{FLASK_PORT}")
    print("=" * 50)
    
    try:
        # Use HTTPS with custom certificate
        ssl_context = None
        
        # Try to use custom certificate if available
        cert_path = os.getenv('SSL_CERT_PATH', '')
        key_path = os.getenv('SSL_KEY_PATH', '')
        
        print(f"🔍 Поиск сертификата...")
        print(f"   SSL_CERT_PATH: {cert_path}")
        print(f"   SSL_KEY_PATH: {key_path}")
        
        if cert_path and key_path:
            if os.path.exists(cert_path) and os.path.exists(key_path):
                ssl_context = (cert_path, key_path)
                print(f"✅ Найден сертификат: {cert_path}")
            else:
                print(f"❌ Файлы сертификата не найдены:")
                print(f"   Сертификат: {cert_path} - {'существует' if os.path.exists(cert_path) else 'НЕ НАЙДЕН'}")
                print(f"   Ключ: {key_path} - {'существует' if os.path.exists(key_path) else 'НЕ НАЙДЕН'}")
                ssl_context = 'adhoc'
                print("⚠️  Используется самоподписной сертификат")
        else:
            print("❌ Пути к сертификату не настроены в .env")
            ssl_context = 'adhoc'
            print("⚠️  Используется самоподписной сертификат")
        
        app.run(
            host=FLASK_HOST,
            port=FLASK_PORT,
            debug=FLASK_DEBUG,
            ssl_context=ssl_context
        )
    except KeyboardInterrupt:
        print("\n🛑 Mini App остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска Mini App: {e}")
        sys.exit(1)