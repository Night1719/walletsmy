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
DEFAULT_TASK_TYPE_ID = int(os.getenv("DEFAULT_TASK_TYPE_ID", "1022"))
DEFAULT_PRIORITY_ID = int(os.getenv("DEFAULT_PRIORITY_ID", "17"))
DEFAULT_WORKFLOW_ID = int(os.getenv("DEFAULT_WORKFLOW_ID", "4"))

# === Email settings ===
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "false").lower() == "true"

# === Corporate email domain ===
CORP_EMAIL_DOMAIN = os.getenv("CORP_EMAIL_DOMAIN", "")

# === OTP settings ===
INSTRUCTIONS_OTP_EXPIRE_MINUTES = int(os.getenv("INSTRUCTIONS_OTP_EXPIRE_MINUTES", "5"))

# === Mini App settings ===
MINIAPP_URL = os.getenv("MINIAPP_URL", "https://your-domain.com:4477/miniapp")
MINIAPP_BOT_TOKEN = os.getenv("MINIAPP_BOT_TOKEN", TELEGRAM_BOT_TOKEN)
MINIAPP_WEBHOOK_URL = os.getenv("MINIAPP_WEBHOOK_URL", "https://your-domain.com:4477")
MINIAPP_MODE = os.getenv("MINIAPP_MODE", "remote")  # local or remote
LINK_EXPIRY_MINUTES = int(os.getenv("LINK_EXPIRY_MINUTES", "40"))

# === Admin settings ===
ADMIN_USER_IDS = [int(x) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip()]

# === Instructions settings ===
INSTRUCTIONS_DIR = os.getenv("INSTRUCTIONS_DIR", "instructions")
INSTRUCTIONS_CONFIG_FILE = os.getenv("INSTRUCTIONS_CONFIG_FILE", "instructions_config.json")

# === File restrictions ===
SCREENSHOT_KEYWORDS = os.getenv("SCREENSHOT_KEYWORDS", "screenshot,screen,shot,скриншот,скрин,снимок").split(",")

# === Video file extensions ===
VIDEO_FILE_EXTENSIONS = os.getenv("VIDEO_FILE_EXTENSIONS", "mp4,avi,mov,wmv,flv,webm,mkv").split(",")

# === Allowed file extensions ===
ALLOWED_FILE_EXTENSIONS = [
    "pdf", "doc", "docx", "txt", "rtf", "odt",
    "mp4", "avi", "mov", "wmv", "flv", "webm", "mkv"
]

# === File size limits ===
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "100"))