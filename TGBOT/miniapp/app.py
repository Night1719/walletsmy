"""
Telegram Mini App for viewing instruction files.
Supports PDF and Word document viewing in Telegram.
"""
import os
import logging
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile
import requests
from config import (
    FILE_SERVER_BASE_URL, FILE_SERVER_USER, FILE_SERVER_PASS, FILE_SERVER_USE_AUTH,
    ALLOWED_FILE_EXTENSIONS, MAX_FILE_SIZE_MB
)
import base64
import hashlib
import hmac
import time
import json

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File server authentication
def _get_auth_headers():
    """Get authentication headers for file server"""
    headers = {}
    if FILE_SERVER_USE_AUTH and FILE_SERVER_USER and FILE_SERVER_PASS:
        credentials = f"{FILE_SERVER_USER}:{FILE_SERVER_PASS}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers["Authorization"] = f"Basic {encoded_credentials}"
    return headers

def _download_file(file_path: str) -> bytes:
    """Download file from file server"""
    if not FILE_SERVER_BASE_URL:
        raise Exception("FILE_SERVER_BASE_URL not configured")
    
    url = f"{FILE_SERVER_BASE_URL.rstrip('/')}/{file_path.lstrip('/')}"
    headers = _get_auth_headers()
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Failed to download file: {response.status_code}")
    except Exception as e:
        logger.error(f"Error downloading file {file_path}: {e}")
        raise

def _validate_telegram_data(init_data: str, bot_token: str) -> bool:
    """Validate Telegram Mini App init data"""
    try:
        # Parse init data
        data = {}
        for item in init_data.split('&'):
            if '=' in item:
                key, value = item.split('=', 1)
                data[key] = value
        
        # Extract hash
        received_hash = data.pop('hash', '')
        if not received_hash:
            return False
        
        # Create data check string
        data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(data.items())])
        
        # Create secret key
        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return calculated_hash == received_hash
    except Exception as e:
        logger.error(f"Error validating Telegram data: {e}")
        return False

# Instruction files mapping
INSTRUCTION_FILES = {
    "1c_ar2": {
        "pdf": "instructions/1c/ar2.pdf",
        "docx": "instructions/1c/ar2.docx"
    },
    "1c_dm": {
        "pdf": "instructions/1c/dm.pdf", 
        "docx": "instructions/1c/dm.docx"
    },
    "email_iphone": {
        "pdf": "instructions/email/iphone.pdf",
        "docx": "instructions/email/iphone.docx"
    },
    "email_android": {
        "pdf": "instructions/email/android.pdf",
        "docx": "instructions/email/android.docx"
    },
    "email_outlook": {
        "pdf": "instructions/email/outlook.pdf",
        "docx": "instructions/email/outlook.docx"
    }
}

@app.route('/')
def index():
    """Main Mini App page"""
    init_data = request.args.get('tgWebAppData', '')
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    # Validate Telegram data
    if not _validate_telegram_data(init_data, bot_token):
        return "Unauthorized", 401
    
    return render_template('index.html')

@app.route('/api/instructions/<instruction_type>')
def get_instruction_files(instruction_type):
    """Get available instruction files for a type"""
    if instruction_type not in INSTRUCTION_FILES:
        return jsonify({"error": "Invalid instruction type"}), 400
    
    available_files = []
    file_paths = INSTRUCTION_FILES[instruction_type]
    
    for format_type, file_path in file_paths.items():
        try:
            # Check if file exists by trying to download it
            content = _download_file(file_path)
            if content:
                available_files.append({
                    "format": format_type,
                    "path": file_path,
                    "size": len(content)
                })
        except Exception as e:
            logger.warning(f"File {file_path} not available: {e}")
            continue
    
    return jsonify({
        "instruction_type": instruction_type,
        "available_files": available_files
    })

@app.route('/api/file/<instruction_type>/<file_format>')
def get_file(instruction_type, file_format):
    """Get instruction file content"""
    if instruction_type not in INSTRUCTION_FILES:
        return jsonify({"error": "Invalid instruction type"}), 400
    
    if file_format not in INSTRUCTION_FILES[instruction_type]:
        return jsonify({"error": "Invalid file format"}), 400
    
    file_path = INSTRUCTION_FILES[instruction_type][file_format]
    
    try:
        content = _download_file(file_path)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_format}") as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Send file
        return send_file(
            tmp_file_path,
            as_attachment=True,
            download_name=f"instruction_{instruction_type}.{file_format}",
            mimetype='application/pdf' if file_format == 'pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        logger.error(f"Error serving file {file_path}: {e}")
        return jsonify({"error": "File not available"}), 404

@app.route('/viewer/<instruction_type>/<file_format>')
def viewer(instruction_type, file_format):
    """File viewer page"""
    init_data = request.args.get('tgWebAppData', '')
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    # Validate Telegram data
    if not _validate_telegram_data(init_data, bot_token):
        return "Unauthorized", 401
    
    if instruction_type not in INSTRUCTION_FILES:
        return "Invalid instruction type", 400
    
    if file_format not in INSTRUCTION_FILES[instruction_type]:
        return "Invalid file format", 400
    
    return render_template('viewer.html', 
                         instruction_type=instruction_type, 
                         file_format=file_format)

@app.route('/api/convert/<instruction_type>/<file_format>')
def convert_file(instruction_type, file_format):
    """Convert file to viewable format"""
    if instruction_type not in INSTRUCTION_FILES:
        return jsonify({"error": "Invalid instruction type"}), 400
    
    if file_format not in INSTRUCTION_FILES[instruction_type]:
        return jsonify({"error": "Invalid file format"}), 400
    
    file_path = INSTRUCTION_FILES[instruction_type][file_format]
    
    try:
        content = _download_file(file_path)
        
        if file_format == 'pdf':
            # For PDF, return base64 encoded content
            return jsonify({
                "type": "pdf",
                "content": base64.b64encode(content).decode(),
                "filename": f"instruction_{instruction_type}.pdf"
            })
        elif file_format in ['docx', 'doc']:
            # For Word documents, we'll need to convert to HTML or PDF
            # For now, return the file as base64
            return jsonify({
                "type": "docx",
                "content": base64.b64encode(content).decode(),
                "filename": f"instruction_{instruction_type}.{file_format}"
            })
        else:
            return jsonify({"error": "Unsupported file format"}), 400
            
    except Exception as e:
        logger.error(f"Error converting file {file_path}: {e}")
        return jsonify({"error": "File conversion failed"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)