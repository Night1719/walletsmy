import requests
import logging
from typing import Optional, Dict, Any, List, Tuple
from config import (
    FILE_SERVER_BASE_URL, FILE_SERVER_USER, FILE_SERVER_PASS, FILE_SERVER_USE_AUTH,
    ALLOWED_FILE_EXTENSIONS, FORBIDDEN_FILE_EXTENSIONS, MAX_FILE_SIZE_MB, ENABLE_CONTENT_VALIDATION
)
import os
import tempfile
import mimetypes
import magic
from file_validator import validate_file_safety

logger = logging.getLogger(__name__)

# Keywords that might indicate screenshot content
SCREENSHOT_KEYWORDS = [
    "screenshot", "скриншот", "screen", "экран", "capture", "захват",
    "print", "печать", "screen_", "img_", "photo", "фото", "picture", "картинка"
]

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
    Get instruction files for a specific type with validation.
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
        
        if content is not None:
            # Validate the file
            is_valid, reason = validate_instruction_file(file_path, content)
            if is_valid:
                result[format_type] = content
                logger.info(f"File {file_path} passed validation: {reason}")
            else:
                logger.warning(f"File {file_path} failed validation: {reason}")
                result[format_type] = None
        else:
            result[format_type] = None
    
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


def _get_file_extension(file_path: str) -> str:
    """Extract file extension from path"""
    return os.path.splitext(file_path)[1].lower().lstrip('.')


def _is_allowed_extension(file_path: str) -> bool:
    """Check if file extension is allowed"""
    ext = _get_file_extension(file_path)
    return ext in ALLOWED_FILE_EXTENSIONS


def _is_forbidden_extension(file_path: str) -> bool:
    """Check if file extension is forbidden"""
    ext = _get_file_extension(file_path)
    return ext in FORBIDDEN_FILE_EXTENSIONS


def _check_file_size(content: bytes) -> bool:
    """Check if file size is within limits"""
    size_mb = len(content) / (1024 * 1024)
    return size_mb <= MAX_FILE_SIZE_MB


def _detect_file_type(content: bytes) -> Optional[str]:
    """Detect actual file type using magic numbers"""
    try:
        mime = magic.from_buffer(content, mime=True)
        return mime
    except Exception as e:
        logger.warning(f"Failed to detect file type: {e}")
        return None


def _is_image_file(mime_type: str) -> bool:
    """Check if file is an image based on MIME type"""
    return mime_type and mime_type.startswith('image/')


def _contains_screenshot_keywords(file_path: str) -> bool:
    """Check if file path contains screenshot-related keywords"""
    filename = os.path.basename(file_path).lower()
    return any(keyword in filename for keyword in SCREENSHOT_KEYWORDS)


def _validate_file_content(content: bytes, file_path: str) -> Tuple[bool, str]:
    """
    Validate file content to detect screenshots and other unwanted content.
    Returns (is_valid, reason)
    """
    if not ENABLE_CONTENT_VALIDATION:
        return True, "Content validation disabled"
    
    # Check file size
    if not _check_file_size(content):
        return False, f"File too large (max {MAX_FILE_SIZE_MB}MB)"
    
    # Detect actual file type
    mime_type = _detect_file_type(content)
    if mime_type and _is_image_file(mime_type):
        return False, "File appears to be an image (screenshot)"
    
    # Check filename for screenshot keywords
    if _contains_screenshot_keywords(file_path):
        return False, "Filename suggests screenshot content"
    
    # Use advanced validation
    try:
        is_safe, reason, findings = validate_file_safety(file_path, content)
        if not is_safe:
            logger.warning(f"File safety validation failed for {file_path}: {reason}")
            if findings:
                logger.warning(f"Detailed findings: {findings}")
            return False, f"{reason}. Details: {', '.join(findings[:3])}"
    
    except Exception as e:
        logger.warning(f"Error in advanced validation: {e}")
        # Fallback to basic validation
        try:
            # Check for common image headers in content
            image_signatures = [
                b'\x89PNG\r\n\x1a\n',  # PNG
                b'\xff\xd8\xff',        # JPEG
                b'GIF87a',              # GIF87a
                b'GIF89a',              # GIF89a
                b'BM',                  # BMP
            ]
            
            for signature in image_signatures:
                if content.startswith(signature):
                    return False, "File contains image data (likely screenshot)"
            
            # Check for screenshot-related metadata in PDFs
            if content.startswith(b'%PDF'):
                content_str = content[:1000].decode('utf-8', errors='ignore').lower()
                screenshot_indicators = [
                    'screenshot', 'screen capture', 'print screen', 'screen shot',
                    'скриншот', 'захват экрана', 'печать экрана'
                ]
                if any(indicator in content_str for indicator in screenshot_indicators):
                    return False, "PDF appears to contain screenshot content"
        
        except Exception as e2:
            logger.warning(f"Error in fallback validation: {e2}")
            return True, "Content validation failed, allowing file"
    
    return True, "File validation passed"


def validate_instruction_file(file_path: str, content: bytes) -> Tuple[bool, str]:
    """
    Comprehensive file validation for instruction files.
    Returns (is_valid, reason)
    """
    # Check file extension
    if not _is_allowed_extension(file_path):
        return False, f"File extension not allowed. Allowed: {', '.join(ALLOWED_FILE_EXTENSIONS)}"
    
    if _is_forbidden_extension(file_path):
        return False, f"File extension forbidden. Forbidden: {', '.join(FORBIDDEN_FILE_EXTENSIONS)}"
    
    # Validate content
    is_valid, reason = _validate_file_content(content, file_path)
    if not is_valid:
        logger.warning(f"File validation failed for {file_path}: {reason}")
        return False, reason
    
    logger.info(f"File validation passed for {file_path}")
    return True, "File validation passed"