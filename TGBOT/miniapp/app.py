"""
Telegram Mini App for viewing instruction files.
Supports PDF and Word document viewing in Telegram.
"""
import os
import logging
import io
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile
import requests
from config import (
    FILE_SERVER_BASE_URL, FILE_SERVER_USER, FILE_SERVER_PASS, FILE_SERVER_USE_AUTH,
    ALLOWED_FILE_EXTENSIONS, MAX_FILE_SIZE_MB, VIDEO_FILE_EXTENSIONS
)
import base64
import hashlib
import hmac
import time
import json
from config_local import (
    is_local_mode, get_local_file_path, check_local_files, 
    get_available_local_files, LOCAL_MINIAPP_URL
)
from secure_links import init_link_manager, get_link_manager

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize secure link manager
init_link_manager(
    secret_key=os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here'),
    link_expiry_minutes=int(os.getenv('LINK_EXPIRY_MINUTES', '40'))
)

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
    """Download file from local storage"""
    # Use local files
    local_path = Path(__file__).parent.parent / file_path
    if not local_path.exists():
        raise Exception(f"Local file not found: {local_path}")
    
    with open(local_path, 'rb') as f:
        return f.read()

def _get_file_type(file_path):
    """Determine file type based on extension"""
    if not file_path:
        return "unknown"
    
    file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
    
    if file_ext in ['pdf']:
        return "pdf"
    elif file_ext in ['docx', 'doc']:
        return "document"
    elif file_ext in VIDEO_FILE_EXTENSIONS:
        return "video"
    elif file_ext in ['txt']:
        return "text"
    else:
        return "unknown"

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

# Dynamic instruction files - loaded from instruction_manager
def get_instruction_files():
    """Get instruction files from instruction_manager"""
    try:
        # Import instruction_manager from parent directory
        import sys
        from pathlib import Path
        parent_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(parent_dir))
        
        from instruction_manager import get_instruction_manager
        instruction_manager = get_instruction_manager()
        
        # Build instruction files mapping
        instruction_files = {}
        categories = instruction_manager.get_all_categories()
        
        for category in categories:
            category_id = category['id']
            instructions = instruction_manager.get_instructions_by_category(category_id)
            
            for instruction in instructions:
                instruction_id = instruction['id']
                key = f"{category_id}_{instruction_id}"
                
                # Get file formats from instruction
                formats = instruction.get('formats', [])
                instruction_files[key] = {}
                
                for file_format in formats:
                    # Construct file path based on instruction structure
                    file_path = f"instructions/{category_id}/{instruction_id}/{instruction['name']}.{file_format}"
                    instruction_files[key][file_format] = file_path
        
        return instruction_files
    except Exception as e:
        logger.error(f"Error loading instruction files: {e}")
        # Return empty dict instead of failing
        return {}

# Load instruction files (with fallback)
try:
    INSTRUCTION_FILES = get_instruction_files()
    if not INSTRUCTION_FILES:
        logger.warning("No instruction files loaded, using test mapping")
        # Test instruction files for development
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
except Exception as e:
    logger.error(f"Failed to load instruction files: {e}")
    INSTRUCTION_FILES = {}

@app.route('/')
def index():
    """Main Mini App page"""
    init_data = request.args.get('tgWebAppData', '')
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    # Validate Telegram data
    if not _validate_telegram_data(init_data, bot_token):
        return "Unauthorized", 401
    
    return render_template('index.html')

@app.route('/secure/<token>')
def secure_viewer(token):
    """Secure viewer for instruction files with temporary access"""
    try:
        # Validate token
        link_manager = get_link_manager()
        payload = link_manager.validate_token(token)
        
        if not payload:
            return render_template('error.html', 
                                 error_title="Ссылка недействительна",
                                 error_message="Ссылка истекла или недействительна. Обратитесь к боту для получения новой ссылки.")
        
        # Record access
        link_manager.record_access(token)
        
        # Extract data from payload
        instruction_type = payload['instruction_type']
        file_format = payload['file_format']
        user_id = payload['user_id']
        
        # Check if instruction type is valid
        if instruction_type not in INSTRUCTION_FILES:
            return render_template('error.html',
                                 error_title="Ошибка",
                                 error_message="Неверный тип инструкции.")
        
        # Render secure viewer
        return render_template('secure_viewer.html', 
                             instruction_type=instruction_type, 
                             file_format=file_format,
                             token=token)
        
    except Exception as e:
        logger.error(f"Error in secure viewer: {e}")
        return render_template('error.html',
                             error_title="Ошибка сервера",
                             error_message="Произошла ошибка при загрузке файла.")

@app.route('/api/secure/create-link', methods=['POST'])
def create_secure_link():
    """Create a secure temporary link for instruction file"""
    try:
        data = request.get_json()
        instruction_data = data.get('instruction_data')  # Format: "category_id_instruction_id"
        file_format = data.get('file_format')
        user_id = data.get('user_id')
        
        if not all([instruction_data, file_format, user_id]):
            return jsonify({"error": "Missing required parameters"}), 400
        
        # Parse instruction_data
        if '_' not in instruction_data:
            return jsonify({"error": "Invalid instruction data format"}), 400
        
        category_id, instruction_id = instruction_data.split('_', 1)
        instruction_type = f"{category_id}_{instruction_id}"
        
        # Keep existing INSTRUCTION_FILES for now
        # TODO: Implement dynamic reloading when instruction_manager is available
        
        if instruction_type not in INSTRUCTION_FILES:
            logger.warning(f"Instruction type {instruction_type} not found in {list(INSTRUCTION_FILES.keys())}")
            return jsonify({"error": "Instruction not found"}), 404
        
        if file_format not in INSTRUCTION_FILES[instruction_type]:
            logger.warning(f"File format {file_format} not found for {instruction_type}")
            return jsonify({"error": "File format not available"}), 404
        
        # Create secure link
        link_manager = get_link_manager()
        base_url = request.url_root.rstrip('/')
        secure_url = link_manager.create_secure_link(
            instruction_type, file_format, user_id, base_url
        )
        
        return jsonify({
            "secure_url": secure_url,
            "expires_in_minutes": link_manager.link_expiry_minutes
        })
        
    except Exception as e:
        logger.error(f"Error creating secure link: {e}")
        return jsonify({"error": "Failed to create secure link"}), 500

@app.route('/api/secure/file/<token>')
def get_secure_file(token):
    """Get instruction file content via secure token"""
    try:
        # Validate token
        link_manager = get_link_manager()
        payload = link_manager.validate_token(token)
        
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        instruction_type = payload['instruction_type']
        file_format = payload['file_format']
        
        # Get file content
        file_path = INSTRUCTION_FILES[instruction_type][file_format]
        content = _download_file(file_path)
        
        # Return file content
        return send_file(
            io.BytesIO(content),
            as_attachment=False,
            download_name=f"instruction_{instruction_type}.{file_format}",
            mimetype='application/pdf' if file_format == 'pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        logger.error(f"Error serving secure file: {e}")
        return jsonify({"error": "File not available"}), 404

@app.route('/api/secure/convert/<token>')
def convert_secure_file(token):
    """Convert secure file to viewable format"""
    try:
        logger.info(f"Converting secure file for token: {token}")
        
        # Validate token
        link_manager = get_link_manager()
        payload = link_manager.validate_token(token)
        
        if not payload:
            logger.warning(f"Invalid or expired token: {token}")
            return jsonify({"error": "Invalid or expired token"}), 401
        
        instruction_type = payload['instruction_type']
        file_format = payload['file_format']
        
        logger.info(f"Processing instruction: {instruction_type}, format: {file_format}")
        
        # Check if instruction exists
        if instruction_type not in INSTRUCTION_FILES:
            logger.error(f"Instruction type not found: {instruction_type}")
            return jsonify({"error": "Instruction not found"}), 404
        
        if file_format not in INSTRUCTION_FILES[instruction_type]:
            logger.error(f"File format not found: {file_format} for {instruction_type}")
            return jsonify({"error": "File format not available"}), 404
        
        # Get file content
        file_path = INSTRUCTION_FILES[instruction_type][file_format]
        logger.info(f"Loading file: {file_path}")
        
        content = _download_file(file_path)
        file_type = _get_file_type(file_path)
        
        logger.info(f"File loaded: {len(content)} bytes, type: {file_type}")
        
        if file_type == 'pdf':
            return jsonify({
                "type": "pdf",
                "content": base64.b64encode(content).decode(),
                "filename": f"instruction_{instruction_type}.pdf"
            })
        elif file_type == 'document':
            return jsonify({
                "type": "docx",
                "content": base64.b64encode(content).decode(),
                "filename": f"instruction_{instruction_type}.{file_format}"
            })
        elif file_type == 'video':
            return jsonify({
                "type": "video",
                "content": base64.b64encode(content).decode(),
                "filename": f"instruction_{instruction_type}.{file_format}",
                "video_format": file_format
            })
        elif file_type == 'text':
            return jsonify({
                "type": "text",
                "content": content.decode('utf-8', errors='ignore'),
                "filename": f"instruction_{instruction_type}.{file_format}"
            })
        else:
            logger.error(f"Unsupported file type: {file_type}")
            return jsonify({"error": "Unsupported file format"}), 400
            
    except Exception as e:
        logger.error(f"Error converting secure file: {e}")
        return jsonify({"error": "File conversion failed"}), 500

@app.route('/api/instructions/<instruction_type>')
def get_instruction_files(instruction_type):
    """Get available instruction files for a type"""
    if instruction_type not in INSTRUCTION_FILES:
        return jsonify({"error": "Invalid instruction type"}), 400
    
    if is_local_mode():
        # Use local files
        available_files = get_available_local_files(instruction_type)
    else:
        # Use file server
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
    app.run(debug=True, host='0.0.0.0', port=4477)