"""
Simple Mini App for testing instruction viewing.
Run this locally for development.
"""
from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from pathlib import Path

app = Flask(__name__)

# Configuration
INSTRUCTIONS_DIR = Path("../instructions")
CONFIG_FILE = Path("../instructions_config.json")

def load_instructions_config():
    """Load instructions configuration"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"categories": {}}
    except Exception as e:
        print(f"Error loading config: {e}")
        return {"categories": {}}

@app.route('/')
def index():
    """Main page"""
    return """
    <h1>Mini App Server</h1>
    <p>Mini App server is running!</p>
    <p><a href="/miniapp">Open Mini App</a></p>
    """

@app.route('/miniapp')
def miniapp():
    """Mini App interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Instructions Mini App</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 600px; margin: 0 auto; }
            .instruction { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .back-btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 Инструкции</h1>
            <p>Mini App работает локально!</p>
            <div class="instruction">
                <h3>✅ Подключение успешно</h3>
                <p>Mini App сервер запущен и готов к работе.</p>
                <p>Для полной функциональности настройте внешний доступ.</p>
            </div>
            <button class="back-btn" onclick="window.close()">Закрыть</button>
        </div>
    </body>
    </html>
    """

@app.route('/secure/<token>')
def secure_viewer(token):
    """Secure instruction viewer"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Инструкция - {token}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .instruction {{ border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 5px; }}
            .back-btn {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 Инструкция</h1>
            <div class="instruction">
                <h3>Токен: {token}</h3>
                <p>Инструкция загружена успешно!</p>
                <p>Это демо-версия Mini App. Для полной функциональности настройте внешний доступ.</p>
            </div>
            <button class="back-btn" onclick="window.close()">Закрыть</button>
        </div>
    </body>
    </html>
    """

@app.route('/api/secure/create-link', methods=['POST'])
def create_secure_link():
    """API endpoint for creating secure links"""
    try:
        data = request.get_json()
        instruction_data = data.get('instruction_data', '')
        file_format = data.get('file_format', '')
        user_id = data.get('user_id', 0)
        
        # Generate simple token
        token = f"{instruction_data}_{file_format}_{user_id}_{int(time.time())}"
        
        return jsonify({
            "success": True,
            "secure_url": f"http://localhost:4477/secure/{token}",
            "token": token
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Запуск Mini App сервера...")
    print("🌐 URL: http://localhost:4477")
    print("📱 Mini App: http://localhost:4477/miniapp")
    print("⏹️  Остановка: Ctrl+C")
    
    app.run(host='0.0.0.0', port=4477, debug=True)