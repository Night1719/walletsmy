import os
import base64

# === Telegram ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# === IntraService API ===
INTRASERVICE_BASE_URL = os.getenv("INTRASERVICE_BASE_URL", "https://helpdesk.bunter.ru/api")
API_VERSION = os.getenv("INTRASERVICE_API_VERSION", "5.42")
INTRASERVICE_USER = os.getenv("INTRASERVICE_USER", "")
INTRASERVICE_PASS = os.getenv("INTRASERVICE_PASS", "")
ENCODED_CREDENTIALS = os.getenv("INTRASERVICE_ENCODED_CREDENTIALS", "")
API_USER_ID = int(os.getenv("API_USER_ID", "0"))  # ID пользователя API для согласования

if not ENCODED_CREDENTIALS and INTRASERVICE_USER and INTRASERVICE_PASS:
    ENCODED_CREDENTIALS = base64.b64encode(f"{INTRASERVICE_USER}:{INTRASERVICE_PASS}".encode()).decode()

# === Services ===
ALLOWED_SERVICES = {
    67: "Удаленный доступ",
    61: "Прочее",
}
ALLOWED_SERVICE_IDS = list(ALLOWED_SERVICES.keys())

# Explicit service IDs for handlers (override-safe)
SERVICE_ID_REMOTE_ACCESS = int(os.getenv("SERVICE_ID_REMOTE_ACCESS", "67"))
SERVICE_ID_MISC = int(os.getenv("SERVICE_ID_MISC", "61"))

# Remote access process specifics
REMOTE_ACCESS_TYPE_ID = int(os.getenv("REMOTE_ACCESS_TYPE_ID", "1022"))
REMOTE_ACCESS_PRIORITY_ID = int(os.getenv("REMOTE_ACCESS_PRIORITY_ID", "17"))
REMOTE_ACCESS_WORKFLOW_ID = int(os.getenv("REMOTE_ACCESS_WORKFLOW_ID", "4"))

# === Files & misc ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_FILE = os.path.join(BASE_DIR, "user_data.json")
USER_PREFERENCES_FILE = os.path.join(BASE_DIR, "user_preferences.json")
TASK_CACHE_FILE = os.path.join(BASE_DIR, "task_cache.json")

HELPDESK_WEB_BASE = os.getenv("HELPDESK_WEB_BASE", "https://helpdesk.bunter.ru/task")
BACKGROUND_POLL_INTERVAL_SEC = int(os.getenv("BACKGROUND_POLL_INTERVAL_SEC", "30"))

# === Logging ===
LOG_DIR = os.getenv("LOG_DIR", os.path.join(BASE_DIR, "logs"))
LOG_FILE = os.getenv("LOG_FILE", os.path.join(LOG_DIR, "bot.log"))

# === Metrics ===
METRICS_PORT = int(os.getenv("METRICS_PORT", "9108"))

# === Task defaults ===
DEFAULT_TYPE_ID = int(os.getenv("DEFAULT_TYPE_ID", "0"))
DEFAULT_PRIORITY_ID = int(os.getenv("DEFAULT_PRIORITY_ID", "0"))
DEFAULT_URGENCY_ID = int(os.getenv("DEFAULT_URGENCY_ID", "0"))
DEFAULT_IMPACT_ID = int(os.getenv("DEFAULT_IMPACT_ID", "0"))

# === Registration request defaults ===
REGISTRATION_SERVICE_ID = int(os.getenv("REGISTRATION_SERVICE_ID", "0"))
REGISTRATION_CREATOR_ID = int(os.getenv("REGISTRATION_CREATOR_ID", "0"))
REGISTRATION_STATUS_ID = int(os.getenv("REGISTRATION_STATUS_ID", "27"))

# === Email/OTP ===
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@example.com")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "false").lower() == "true"

CORP_EMAIL_DOMAIN = os.getenv("CORP_EMAIL_DOMAIN", "")  # например bunter.ru
OTP_EXPIRE_MINUTES = int(os.getenv("OTP_EXPIRE_MINUTES", "10"))

# === File Server ===
FILE_SERVER_BASE_URL = os.getenv("FILE_SERVER_BASE_URL", "")
FILE_SERVER_USER = os.getenv("FILE_SERVER_USER", "")
FILE_SERVER_PASS = os.getenv("FILE_SERVER_PASS", "")
FILE_SERVER_USE_AUTH = os.getenv("FILE_SERVER_USE_AUTH", "false").lower() == "true"

# === Instructions OTP ===
INSTRUCTIONS_OTP_EXPIRE_MINUTES = int(os.getenv("INSTRUCTIONS_OTP_EXPIRE_MINUTES", "5"))

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
