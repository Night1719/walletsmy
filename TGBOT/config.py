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

if not ENCODED_CREDENTIALS and INTRASERVICE_USER and INTRASERVICE_PASS:
    ENCODED_CREDENTIALS = base64.b64encode(f"{INTRASERVICE_USER}:{INTRASERVICE_PASS}".encode()).decode()

# === Services ===
ALLOWED_SERVICES = {
    1: "Не работает ПК",
    2: "Удаленный доступ",
    3: "Прочее",
}
ALLOWED_SERVICE_IDS = list(ALLOWED_SERVICES.keys())

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