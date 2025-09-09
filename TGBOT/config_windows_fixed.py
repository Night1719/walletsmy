"""
Configuration file for Telegram Bot with dynamic instructions.
Fixed version for Windows users.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === Telegram Bot ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is required")

# === IntraService API ===
INTRASERVICE_BASE_URL = os.getenv("INTRASERVICE_BASE_URL", "")
INTRASERVICE_USER = os.getenv("INTRASERVICE_USER", "")
INTRASERVICE_PASS = os.getenv("INTRASERVICE_PASS", "")
API_USER_ID = os.getenv("API_USER_ID", "")

# === Email Configuration ===
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "false").lower() == "true"
CORP_EMAIL_DOMAIN = os.getenv("CORP_EMAIL_DOMAIN", "")

# === Logging ===
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILE = os.path.join(LOG_DIR, "bot.log")

# === Metrics ===
METRICS_PORT = int(os.getenv("METRICS_PORT", "9090"))

# === Services ===
ALLOWED_SERVICES = os.getenv("ALLOWED_SERVICES", "helpdesk,it,hr,finance").split(",")

# === OTP Configuration ===
OTP_EXPIRE_MINUTES = int(os.getenv("OTP_EXPIRE_MINUTES", "10"))
INSTRUCTIONS_OTP_EXPIRE_MINUTES = int(os.getenv("INSTRUCTIONS_OTP_EXPIRE_MINUTES", "5"))

# === File Server Configuration ===
FILE_SERVER_BASE_URL = os.getenv("FILE_SERVER_BASE_URL", "")
FILE_SERVER_USER = os.getenv("FILE_SERVER_USER", "")
FILE_SERVER_PASS = os.getenv("FILE_SERVER_PASS", "")
FILE_SERVER_USE_AUTH = os.getenv("FILE_SERVER_USE_AUTH", "false").lower() == "true"

# === Admin Configuration ===
ADMIN_USER_IDS = [int(x) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip()]
INSTRUCTIONS_DIR = os.getenv("INSTRUCTIONS_DIR", "instructions")
INSTRUCTIONS_CONFIG_FILE = os.getenv("INSTRUCTIONS_CONFIG_FILE", "instructions_config.json")

# === Telegram Mini App ===
MINIAPP_URL = os.getenv("MINIAPP_URL", "https://your-domain.com/miniapp")
MINIAPP_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")  # Same as bot token
MINIAPP_WEBHOOK_URL = os.getenv("MINIAPP_WEBHOOK_URL", "https://your-domain.com")
MINIAPP_MODE = os.getenv("MINIAPP_MODE", "remote")  # local or remote
LINK_EXPIRY_MINUTES = int(os.getenv("LINK_EXPIRY_MINUTES", "40"))  # Secure link expiry time

# === File Restrictions ===
# Allowed file extensions for instructions
ALLOWED_FILE_EXTENSIONS = os.getenv("ALLOWED_FILE_EXTENSIONS", "pdf,docx,doc,txt").split(",")
# Forbidden file extensions (screenshots, images, etc.)
FORBIDDEN_FILE_EXTENSIONS = os.getenv("FORBIDDEN_FILE_EXTENSIONS", "png,jpg,jpeg,gif,bmp,tiff,webp,ico,svg,psd,ai,sketch").split(",")
# Maximum file size in MB
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
# Enable content validation (check for screenshots in files)
ENABLE_CONTENT_VALIDATION = os.getenv("ENABLE_CONTENT_VALIDATION", "true").lower() == "true"
# Keywords that indicate screenshot files
SCREENSHOT_KEYWORDS = os.getenv("SCREENSHOT_KEYWORDS", "screenshot,screen,shot,скриншот,скрин,снимок").split(",")