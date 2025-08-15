import requests
import logging
from config import INTRASERVICE_BASE_URL, ENCODED_CREDENTIALS, API_VERSION

# Отключаем предупреждения о самоподписанном сертификате (для теста)
requests.packages.urllib3.disable_warnings()

logger = logging.getLogger(__name__)


# --- 1. ПОИСК ПОЛЬЗОВАТЕЛЯ ПО ТЕЛЕФОНУ ---
def get_user_by_phone(phone: str):
    """
    Найти пользователя по номеру телефона.
    Поддерживаем форматы: +7..., 8..., 7...
    """
    # Нормализуем номер
    digits = ''.join(filter(str.isdigit, phone))
    if not digits:
        return None

    search_query = None
    if digits.startswith('8') and len(digits) == 11:
        search_query = digits[1:]  # 89506459087 → 9506459087
    elif digits.startswith('7') and len(digits) == 11:
        search_query = digits[1:]  # 79506459087 → 9506459087
    elif len(digits) == 10:
        search_query = digits  # 9506459087

    if not search_query:
        return None

    url = f"{INTRASERVICE_BASE_URL}/user"
    headers = {
        "Authorization": f"Basic {ENCODED_CREDENTIALS}",
        "Accept": "application/json",
        "X-API-Version": API_VERSION,
    }
    params = {"search": search_query}

    try:
        response = requests.get(url, headers=headers, params=params, verify=False)
        logger.info(f"🔍 Поиск пользователя: {params} → статус {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            users = data.get("Users", [])
            for user in users:
                mp = user.get("MobilePhone", "")
                if not mp:
                    continue
                mp_digits = ''.join(filter(str.isdigit, mp))
                if mp_digits.startswith('8') and len(mp_digits) == 11:
                    mp_digits = '7' + mp_digits[1:]
                if mp_digits == '7' + search_query:
                    logger.info(f"✅ Найден пользователь: {user['Name']} (ID={user['Id']})")
                    return user
        else:
            logger.error(f"❌ Ошибка API: {response.status_code} {response.text}")
    except Exception as e:
        logger.error(f"❌ Ошибка поиска пользователя: {e}")
    return None


# --- 2. ПОЛУЧЕНИЕ ЗАЯВОК ПОЛЬЗОВАТЕЛЯ ---
def get_user_tasks(user_id: int, status_filter: str = "open"):
    """
    Получить заявки пользователя.
    status_filter: "open" или "closed"
    """
    url = f"{INTRASERVICE_BASE_URL}/task"
    headers = {
        "Authorization": f"Basic {ENCODED_CREDENTIALS}",
        "Accept": "application/json",
        "X-API-Version": API_VERSION,
    }

    # ID статусов
    open_ids = "27,31,35,44"   # Новая, Открыта, В работе, Ожидает
    closed_ids = "28,29,30"     # Завершена, Выполнена, Отклонена

    params = {
        "creatorids": user_id,
        "statusids": open_ids if status_filter == "open" else closed_ids,
        "count": "false"
    }

    try:
        response = requests.get(url, headers=headers, params=params, verify=False)
        logger.info(f"📡 GET /task | URL: {response.url}")

        if response.status_code == 200:
            return response.json().get("Tasks", [])
        else:
            logger.error(f"❌ Ошибка получения заявок: {response.status_code} {response.text}")
            return []
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return []


# --- 3. ПОЛУЧЕНИЕ ЗАЯВОК НА СОГЛАСОВАНИЕ ---
def get_tasks_awaiting_approval(user_intraservice_id: int):
    """
    Получить заявки, где пользователь — согласующий и ещё не согласовал.
    Учитывает CoordinatorIds и IsCoordinatedForCoordinators.
    """
    url = f"{INTRASERVICE_BASE_URL}/task"
    headers = {
        "Authorization": f"Basic {ENCODED_CREDENTIALS}",
        "Accept": "application/json",
        "X-API-Version": API_VERSION,
    }
    params = {
        "coordinatorids": user_intraservice_id,
        "statusids": "36",  # Статус "Согласование"
        "count": "false"
    }

    try:
        response = requests.get(url, headers=headers, params=params, verify=False)
        if response.status_code != 200:
            logger.error(f"❌ Ошибка получения заявок на согласование: {response.status_code}")
            return []

        tasks = response.json().get("Tasks", [])
        result = []

        for task in tasks:
            coordinator_ids_str = task.get("CoordinatorIds", "")
            is_coordinated_str = task.get("IsCoordinatedForCoordinators", "")

            coordinator_ids = [cid.strip() for cid in coordinator_ids_str.split(",") if cid.strip()]
            is_coordinated = [ic.strip().lower() for ic in is_coordinated_str.split(",") if ic.strip()]

            user_id_str = str(user_intraservice_id)

            if user_id_str not in coordinator_ids:
                continue  # Не вы

            idx = coordinator_ids.index(user_id_str)
            if idx < len(is_coordinated) and is_coordinated[idx] == "true":
                continue  # Уже согласовали

            result.append(task)

        logger.info(f"✅ Найдено {len(result)} заявок на согласование")
        return result

    except Exception as e:
        logger.error(f"❌ Ошибка при получении заявок на согласование: {e}")
        return []


# --- 4. ПОЛУЧЕНИЕ ДЕТАЛЕЙ ЗАЯВКИ ---
def get_task_details(task_id: int):
    """
    Получить детали заявки + комментарии.
    """
    url = f"{INTRASERVICE_BASE_URL}/task/{task_id}"
    headers = {
        "Authorization": f"Basic {ENCODED_CREDENTIALS}",
        "Accept": "application/json",
        "X-API-Version": API_VERSION,
    }
    params = {"include": "COMMENTS"}

    try:
        response = requests.get(url, headers=headers, params=params, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"❌ Ошибка получения заявки #{task_id}: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return None


# --- 5. ДОБАВЛЕНИЕ КОММЕНТАРИЯ ---
def add_comment_to_task(task_id: int, comment: str):
    """
    Добавить комментарий к заявке.
    """
    url = f"{INTRASERVICE_BASE_URL}/task/{task_id}"
    headers = {
        "Authorization": f"Basic {ENCODED_CREDENTIALS}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Version": API_VERSION,
    }
    payload = {"Comment": comment}

    try:
        response = requests.put(url, headers=headers, json=payload, verify=False)
        if response.status_code == 200:
            logger.info(f"✅ Комментарий добавлен к заявке #{task_id}")
            return True
        else:
            logger.error(f"❌ Ошибка добавления комментария: {response.status_code} {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return False


# --- 6. СОГЛАСОВАНИЕ / ОТКЛОНЕНИЕ ЗАЯВКИ ---
def approve_task(task_id: int, approve: bool = True, comment: str = "", user_name: str = None):
    """
    Согласовать или отклонить заявку.
    """
    url = f"{INTRASERVICE_BASE_URL}/task/{task_id}"
    headers = {
        "Authorization": f"Basic {ENCODED_CREDENTIALS}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Version": API_VERSION,
    }

    full_comment = comment or ""
    if user_name:
        action = "Согласовано" if approve else "Отклонено"
        full_comment = f"{action} через Telegram пользователем: {user_name}. {full_comment}".strip()

    payload = {"Coordinate": approve}
    if full_comment:
        payload["Comment"] = full_comment

    try:
        response = requests.put(url, headers=headers, json=payload, verify=False)
        if response.status_code == 200:
            logger.info(f"✅ Заявка #{task_id} {'согласована' if approve else 'отклонена'}")
            return True
        else:
            logger.error(f"❌ Ошибка согласования: {response.status_code} {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return False


# --- 7. СОЗДАНИЕ НОВОЙ ЗАЯВКИ ---
def create_task(**payload):
    """
    Создать новую заявку.
    Пример payload:
    {
        "Name": "Новая заявка",
        "Description": "Описание",
        "CreatorId": 53,
        "ServiceId": 1,
        "StatusId": 27
    }
    """
    url = f"{INTRASERVICE_BASE_URL}/task"
    headers = {
        "Authorization": f"Basic {ENCODED_CREDENTIALS}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Version": API_VERSION,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, verify=False)
        if response.status_code == 201:
            task_id = response.json().get("Id")
            logger.info(f"✅ Заявка создана: #{task_id}")
            return task_id
        else:
            logger.error(f"❌ Ошибка создания заявки: {response.status_code} {response.text}")
            return None
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return None