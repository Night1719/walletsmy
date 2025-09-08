"""
Local configuration for Telegram Mini App
This allows running Mini App locally without internet access
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Local file storage
LOCAL_FILES_DIR = BASE_DIR / "local_files"
LOCAL_FILES_DIR.mkdir(exist_ok=True)

# Instruction files mapping for local storage
LOCAL_INSTRUCTION_FILES = {
    "1c_ar2": {
        "pdf": LOCAL_FILES_DIR / "1c_ar2.pdf",
        "docx": LOCAL_FILES_DIR / "1c_ar2.docx"
    },
    "1c_dm": {
        "pdf": LOCAL_FILES_DIR / "1c_dm.pdf", 
        "docx": LOCAL_FILES_DIR / "1c_dm.docx"
    },
    "email_iphone": {
        "pdf": LOCAL_FILES_DIR / "email_iphone.pdf",
        "docx": LOCAL_FILES_DIR / "email_iphone.docx"
    },
    "email_android": {
        "pdf": LOCAL_FILES_DIR / "email_android.pdf",
        "docx": LOCAL_FILES_DIR / "email_android.docx"
    },
    "email_outlook": {
        "pdf": LOCAL_FILES_DIR / "email_outlook.pdf",
        "docx": LOCAL_FILES_DIR / "email_outlook.docx"
    }
}

# Local Mini App settings
LOCAL_MINIAPP_URL = "http://localhost:5000/miniapp"
LOCAL_BOT_TOKEN = "your_bot_token_here"  # Set this in your .env

# Check if running locally
def is_local_mode():
    """Check if running in local mode (no internet required)"""
    return os.getenv('MINIAPP_MODE', 'local').lower() == 'local'

def get_local_file_path(instruction_type: str, file_format: str) -> Path:
    """Get local file path for instruction"""
    if instruction_type not in LOCAL_INSTRUCTION_FILES:
        raise ValueError(f"Unknown instruction type: {instruction_type}")
    
    if file_format not in LOCAL_INSTRUCTION_FILES[instruction_type]:
        raise ValueError(f"Unknown file format: {file_format}")
    
    return LOCAL_INSTRUCTION_FILES[instruction_type][file_format]

def check_local_files():
    """Check which local files are available"""
    available_files = {}
    
    for instruction_type, formats in LOCAL_INSTRUCTION_FILES.items():
        available_files[instruction_type] = {}
        for file_format, file_path in formats.items():
            available_files[instruction_type][file_format] = file_path.exists()
    
    return available_files

def get_available_local_files(instruction_type: str):
    """Get available local files for instruction type"""
    if instruction_type not in LOCAL_INSTRUCTION_FILES:
        return []
    
    available = []
    for file_format, file_path in LOCAL_INSTRUCTION_FILES[instruction_type].items():
        if file_path.exists():
            available.append({
                "format": file_format,
                "path": str(file_path),
                "size": file_path.stat().st_size if file_path.exists() else 0
            })
    
    return available