#!/usr/bin/env python3
"""
Run Mini App with ngrok tunnel for external access
"""
import os
import sys
import subprocess
import time
import threading
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

def run_ngrok():
    """Run ngrok tunnel"""
    try:
        print("🌐 Запуск ngrok туннеля...")
        subprocess.run([
            "ngrok", "http", str(FLASK_PORT), 
            "--host-header=rewrite"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка запуска ngrok: {e}")
        print("💡 Установите ngrok: https://ngrok.com/download")
    except FileNotFoundError:
        print("❌ ngrok не найден")
        print("💡 Установите ngrok: https://ngrok.com/download")

def run_flask():
    """Run Flask app"""
    try:
        print("🚀 Запуск Mini App...")
        app.run(
            host=FLASK_HOST,
            port=FLASK_PORT,
            debug=FLASK_DEBUG,
            ssl_context='adhoc'
        )
    except KeyboardInterrupt:
        print("\n🛑 Mini App остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска Mini App: {e}")

if __name__ == '__main__':
    print("🔧 Запуск Mini App с ngrok туннелем")
    print("=" * 50)
    print(f"📍 Хост: {FLASK_HOST}")
    print(f"🔌 Порт: {FLASK_PORT}")
    print(f"🌐 URL: https://127.0.0.1:{FLASK_PORT}")
    print("=" * 50)
    
    # Check if ngrok is available
    try:
        subprocess.run(["ngrok", "version"], capture_output=True, check=True)
        print("✅ ngrok найден")
        
        # Start ngrok in background
        ngrok_thread = threading.Thread(target=run_ngrok, daemon=True)
        ngrok_thread.start()
        
        # Wait a bit for ngrok to start
        time.sleep(3)
        
        print("\n💡 Получите публичный URL из ngrok интерфейса:")
        print("   http://127.0.0.1:4040")
        print("\n📝 Обновите MINIAPP_URL в .env файле на ngrok URL")
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  ngrok не найден, запуск без туннеля")
        print("💡 Для внешнего доступа установите ngrok")
    
    # Run Flask app
    run_flask()