@echo off
echo ========================================
echo    Запуск Mini App сервера
echo ========================================
echo.

echo 🚀 Запуск Mini App на порту 4477...
cd miniapp

if exist "simple_app.py" (
    echo ✅ Найден simple_app.py
    python simple_app.py
) else (
    echo ❌ simple_app.py не найден
    echo Создание простого сервера...
    
    echo from flask import Flask, render_template, request, jsonify > simple_app.py
    echo import time >> simple_app.py
    echo. >> simple_app.py
    echo app = Flask(__name__) >> simple_app.py
    echo. >> simple_app.py
    echo @app.route('/') >> simple_app.py
    echo def index(): >> simple_app.py
    echo     return "Mini App Server Running" >> simple_app.py
    echo. >> simple_app.py
    echo @app.route('/miniapp') >> simple_app.py
    echo def miniapp(): >> simple_app.py
    echo     return "Mini App Interface" >> simple_app.py
    echo. >> simple_app.py
    echo @app.route('/api/secure/create-link', methods=['POST']) >> simple_app.py
    echo def create_secure_link(): >> simple_app.py
    echo     data = request.get_json() >> simple_app.py
    echo     instruction_data = data.get('instruction_data', '') >> simple_app.py
    echo     file_format = data.get('file_format', '') >> simple_app.py
    echo     user_id = data.get('user_id', 0) >> simple_app.py
    echo     token = f"{instruction_data}_{file_format}_{user_id}_{int(time.time())}" >> simple_app.py
    echo     return jsonify({"success": True, "secure_url": f"http://localhost:4477/secure/{token}", "token": token}) >> simple_app.py
    echo. >> simple_app.py
    echo @app.route('/secure/<token>') >> simple_app.py
    echo def secure_viewer(token): >> simple_app.py
    echo     return f"Secure Viewer: {token}" >> simple_app.py
    echo. >> simple_app.py
    echo if __name__ == '__main__': >> simple_app.py
    echo     app.run(host='0.0.0.0', port=4477, debug=True) >> simple_app.py
    
    echo ✅ Простой сервер создан
    python simple_app.py
)

echo.
echo Mini App остановлен
pause