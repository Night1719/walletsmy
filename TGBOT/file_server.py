import requests
import logging
from typing import Optional, Dict, Any
from config import FILE_SERVER_BASE_URL, FILE_SERVER_USER, FILE_SERVER_PASS, FILE_SERVER_USE_AUTH
import os
import tempfile

logger = logging.getLogger(__name__)

# Mapping of instruction types to file paths on the server
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


def _get_auth_headers() -> Dict[str, str]:
    """Get authentication headers for file server"""
    headers = {}
    if FILE_SERVER_USE_AUTH and FILE_SERVER_USER and FILE_SERVER_PASS:
        import base64
        credentials = f"{FILE_SERVER_USER}:{FILE_SERVER_PASS}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers["Authorization"] = f"Basic {encoded_credentials}"
    return headers


def _download_file(file_path: str) -> Optional[bytes]:
    """Download file from file server"""
    if not FILE_SERVER_BASE_URL:
        logger.error("FILE_SERVER_BASE_URL not configured")
        return None
    
    url = f"{FILE_SERVER_BASE_URL.rstrip('/')}/{file_path.lstrip('/')}"
    headers = _get_auth_headers()
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.content
        else:
            logger.error(f"Failed to download file {file_path}: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error downloading file {file_path}: {e}")
        return None


def get_instruction_files(instruction_type: str) -> Dict[str, Optional[bytes]]:
    """
    Get instruction files for a specific type.
    Returns dict with 'pdf' and 'docx' keys containing file content or None.
    """
    if instruction_type not in INSTRUCTION_FILES:
        logger.error(f"Unknown instruction type: {instruction_type}")
        return {"pdf": None, "docx": None}
    
    file_paths = INSTRUCTION_FILES[instruction_type]
    result = {}
    
    for format_type, file_path in file_paths.items():
        logger.info(f"Downloading {instruction_type} {format_type} from {file_path}")
        content = _download_file(file_path)
        result[format_type] = content
    
    return result


def save_temp_file(content: bytes, extension: str) -> Optional[str]:
    """Save file content to temporary file and return path"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}") as tmp_file:
            tmp_file.write(content)
            return tmp_file.name
    except Exception as e:
        logger.error(f"Error saving temp file: {e}")
        return None


def cleanup_temp_file(file_path: str) -> None:
    """Clean up temporary file"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        logger.error(f"Error cleaning up temp file {file_path}: {e}")


def get_instruction_info(instruction_type: str) -> Dict[str, Any]:
    """Get information about available instruction files"""
    if instruction_type not in INSTRUCTION_FILES:
        return {"available": False, "formats": []}
    
    file_paths = INSTRUCTION_FILES[instruction_type]
    available_formats = []
    
    for format_type, file_path in file_paths.items():
        if _download_file(file_path) is not None:
            available_formats.append(format_type)
    
    return {
        "available": len(available_formats) > 0,
        "formats": available_formats,
        "file_paths": file_paths
    }