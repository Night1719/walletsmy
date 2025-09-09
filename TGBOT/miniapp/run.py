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

# Import and run the app
from app import app
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG

if __name__ == '__main__':
    print("🚀 Запуск Telegram Mini App...")
    print(f"📍 Хост: {FLASK_HOST}")
    print(f"🔌 Порт: {FLASK_PORT}")
    print(f"🐛 Режим отладки: {FLASK_DEBUG}")
    print(f"🌐 URL: http://{FLASK_HOST}:{FLASK_PORT}")
    print("=" * 50)
    
    try:
        app.run(
            host=FLASK_HOST,
            port=FLASK_PORT,
            debug=FLASK_DEBUG,
            ssl_context='adhoc' if os.getenv('USE_SSL', 'false').lower() == 'true' else None
        )
    except KeyboardInterrupt:
        print("\n🛑 Mini App остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска Mini App: {e}")
        sys.exit(1)