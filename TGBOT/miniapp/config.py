"""
Configuration for Telegram Mini App
"""
import os

# === File Server Configuration ===
FILE_SERVER_BASE_URL = os.getenv("FILE_SERVER_BASE_URL", "")
FILE_SERVER_USER = os.getenv("FILE_SERVER_USER", "")
FILE_SERVER_PASS = os.getenv("FILE_SERVER_PASS", "")
FILE_SERVER_USE_AUTH = os.getenv("FILE_SERVER_USE_AUTH", "false").lower() == "true"

# === File Restrictions ===
ALLOWED_FILE_EXTENSIONS = os.getenv("ALLOWED_FILE_EXTENSIONS", "pdf,docx,doc,txt,mp4,avi,mov,wmv,flv,webm,mkv").split(",")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
VIDEO_FILE_EXTENSIONS = os.getenv("VIDEO_FILE_EXTENSIONS", "mp4,avi,mov,wmv,flv,webm,mkv").split(",")

# === Mini App Configuration ===
MINIAPP_URL = os.getenv("MINIAPP_URL", "http://localhost:4477/miniapp")
MINIAPP_MODE = os.getenv("MINIAPP_MODE", "local")  # local or remote
LINK_EXPIRY_MINUTES = int(os.getenv("LINK_EXPIRY_MINUTES", "40"))

# === SSL Configuration ===
SSL_VERIFY = os.getenv("SSL_VERIFY", "false").lower() == "true"
SSL_VERIFY_CERT = os.getenv("SSL_VERIFY_CERT", "false").lower() == "true"
SSL_VERIFY_HOSTNAME = os.getenv("SSL_VERIFY_HOSTNAME", "false").lower() == "true"
SSL_CERT_PATH = os.getenv("SSL_CERT_PATH", "")
SSL_KEY_PATH = os.getenv("SSL_KEY_PATH", "")
SSL_PASSWORD = os.getenv("SSL_PASSWORD", "")

# === Flask Configuration ===
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "your-secret-key-here")
FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("FLASK_PORT", "4477"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# === Telegram Configuration ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# === Local Mode Configuration ===
LOCAL_INSTRUCTIONS_DIR = os.getenv("LOCAL_INSTRUCTIONS_DIR", "../instructions")
LOCAL_MINIAPP_URL = os.getenv("LOCAL_MINIAPP_URL", "http://localhost:4477")