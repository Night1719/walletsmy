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