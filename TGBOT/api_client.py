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

    # Берём последние 10 цифр для поиска
    search_query = digits[-10:] if len(digits) >= 10 else None

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
                # Проверяем все возможные телефонные поля
                phones = []
                for k in ("MobilePhone", "Mobile", "Phone", "Phones", "WorkPhone", "InternalPhone"):
                    v = user.get(k)
                    if isinstance(v, str) and v:
                        phones.append(v)
                match = False
                for p in phones:
                    d = ''.join(filter(str.isdigit, p))
                    if not d:
                        continue
                    last10 = d[-10:] if len(d) >= 10 else d
                    if last10 == search_query or ('7'+last10) == d or ('8'+last10) == d:
                        match = True
                        break
                if match:
                    logger.info(f"✅ Найден пользователь: {user.get('Name')} (ID={user.get('Id')})")
                    return user
            # Если единственный результат и не удалось сопоставить номер — вернём первого как фолбек
            if len(users) == 1:
                u = users[0]
                logger.info(f"ℹ️ Фолбек: возвращаю первого пользователя {u.get('Name')} (ID={u.get('Id')})")
                return u
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
    closed_ids = "28,29,30,45"     # Завершена, Выполнена, Отклонена, Согласовано

    base_params = {
        "statusids": open_ids if status_filter == "open" else closed_ids,
        "count": "false"
    }

    try:
        # 1) Поиск по создателю
        params1 = dict(base_params, creatorids=user_id)
        response = requests.get(url, headers=headers, params=params1, verify=False)
        logger.info(f"📡 GET /task | URL: {response.url}")

        if response.status_code == 200:
            tasks = response.json().get("Tasks", [])
            if tasks:
                return tasks
        else:
            logger.error(f"❌ Ошибка получения заявок: {response.status_code} {response.text}")

        # 2) Фолбек по участию (memberids)
        params2 = dict(base_params, memberids=user_id)
        response = requests.get(url, headers=headers, params=params2, verify=False)
        logger.info(f"📡 GET /task (memberids) | URL: {response.url}")
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
    Получить детали заявки + комментарии. Пытаемся разными include-значениями.
    """
    base_url = f"{INTRASERVICE_BASE_URL}/task/{task_id}"
    headers = {
        "Authorization": f"Basic {ENCODED_CREDENTIALS}",
        "Accept": "application/json",
        "X-API-Version": API_VERSION,
    }
    include_variants = [
        "COMMENTS",
        "TASKCOMMENTS",
        "COMMENTSALL",
    ]

    for inc in include_variants:
        try:
            params = {"include": inc}
            response = requests.get(base_url, headers=headers, params=params, verify=False)
            if response.status_code == 200:
                data = response.json()
                # Если видим поле Comments в любом виде — возвращаем
                if any(k in data for k in ("Comments", "TaskComments", "CommentsList")):
                    return data
                # Даже если нет явного списка, вернём как есть (для статуса/описания)
                if inc == include_variants[-1]:
                    return data
            else:
                logger.error(f"❌ Ошибка получения заявки #{task_id} (include={inc}): {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")

    return None


def get_task_comments(task_id: int):
    """
    Получить список комментариев напрямую, если include не отдаёт.
    Пробуем несколько вариантов путей и структур.
    Возвращает list[dict] или пустой список.
    """
    headers = {
        "Authorization": f"Basic {ENCODED_CREDENTIALS}",
        "Accept": "application/json",
        "X-API-Version": API_VERSION,
    }
    paths = [
        f"{INTRASERVICE_BASE_URL}/task/{task_id}/comment",
        f"{INTRASERVICE_BASE_URL}/task/{task_id}/comments",
    ]
    for url in paths:
        try:
            r = requests.get(url, headers=headers, verify=False)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list):
                    return data
                if isinstance(data, dict):
                    for key in ("Comments", "Items", "TaskComments", "List"):
                        val = data.get(key)
                        if isinstance(val, list):
                            return val
        except Exception:
            logger.exception("❌ Ошибка при получении комментариев для #%s", task_id)
    return []


def get_task_lifetime_comments(task_id: int):
    """
    Получить комментарии из ленты жизни заявки (/tasklifetime).
    Возвращает list[dict] с полями Id, Comments, Author/AuthorName/AuthorIsOperator и пр.
    """
    base = f"{INTRASERVICE_BASE_URL}/tasklifetime"
    headers = {
        "Authorization": f"Basic {ENCODED_CREDENTIALS}",
        "Accept": "application/json",
        "X-API-Version": API_VERSION,
    }
    params = {"taskid": task_id, "lastcommentsontop": "true"}
    try_versions = [headers.copy()]

    # Если текущая версия не отдаёт, попробуем без заголовка X-API-Version или с 1.0
    alt_headers = headers.copy(); alt_headers.pop("X-API-Version", None)
    try_versions.append(alt_headers)
    v1_headers = headers.copy(); v1_headers["X-API-Version"] = "1.0"
    try_versions.append(v1_headers)

    for h in try_versions:
        try:
            r = requests.get(base, headers=h, params=params, verify=False)
            if r.status_code == 200:
                data = r.json()
                items = data.get("TaskLifetimes", [])
                if isinstance(items, list):
                    return items
            else:
                logger.warning(f"⚠️ tasklifetime {r.status_code}: {r.text[:200]}")
        except Exception as e:
            logger.exception("❌ Ошибка tasklifetime для #%s: %s", task_id, e)
    return []


# --- 5. ДОБАВЛЕНИЕ КОММЕНТАРИЯ ---
def add_comment_to_task(task_id: int, comment: str, public: bool = True):
    """
    Добавить комментарий к заявке.
    public=True — попытка создать общедоступный комментарий (включаем несколько флагов на случай разных настроек API)
    """
    url = f"{INTRASERVICE_BASE_URL}/task/{task_id}"
    headers = {
        "Authorization": f"Basic {ENCODED_CREDENTIALS}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Version": API_VERSION,
    }
    payload = {"Comment": comment}

    if public:
        # Возможные поля для публичности комментария (оставлены сразу несколько, лишние будут проигнорированы)
        payload.update({
            "IsPublic": True,
            "IsClientVisible": True,
            "ForClient": True,
            "Internal": False,
            "IsHidden": False,
        })

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
def approve_task(task_id: int, approve: bool = True, comment: str = "", user_name: str = None, coordinator_id: int = None, set_status_on_success: int | None = None):
    """
    Согласовать или отклонить заявку.
    coordinator_id — Id согласующего в IntraService (для выбора конкретного согласующего)
    set_status_on_success — при успехе дополнительно установить указанный StatusId (например 45)
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

    # Пробуем указать конкретного согласующего (если API поддерживает)
    if coordinator_id is not None:
        payload["CoordinatorId"] = coordinator_id
        payload["CoordinateForCoordinatorId"] = coordinator_id

    if full_comment:
        payload["Comment"] = full_comment

    try:
        response = requests.put(url, headers=headers, json=payload, verify=False)
        if response.status_code == 200:
            logger.info(f"✅ Заявка #{task_id} {'согласована' if approve else 'отклонена'}")

            # Опционально выставим статус явно, если нужно (подстроиться под процесс)
            if set_status_on_success is not None and approve:
                try:
                    force_payload = {"StatusId": set_status_on_success}
                    r2 = requests.put(url, headers=headers, json=force_payload, verify=False)
                    if r2.status_code != 200:
                        logger.warning(f"⚠️ Не удалось принудительно установить статус {set_status_on_success} для #{task_id}: {r2.status_code} {r2.text}")
                except Exception as ie:
                    logger.error(f"❌ Ошибка установки статуса: {ie}")
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
        # Удалим None, чтобы не отправлять null на сервер для non-null полей
        clean_payload = {k: v for k, v in payload.items() if v is not None}
        response = requests.post(url, headers=headers, json=clean_payload, verify=False)
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


def search_users_by_name(query: str):
    """
    Поиск пользователей по части имени/фамилии.
    Возвращает список пользователей с основными полями.
    """
    url = f"{INTRASERVICE_BASE_URL}/user"
    headers = {
        "Authorization": f"Basic {ENCODED_CREDENTIALS}",
        "Accept": "application/json",
        "X-API-Version": API_VERSION,
    }
    params = {"search": query}
    try:
        r = requests.get(url, headers=headers, params=params, verify=False)
        if r.status_code == 200:
            return r.json().get("Users", [])
        else:
            logger.error(f"❌ Ошибка поиска сотрудников: {r.status_code} {r.text}")
            return []
    except Exception as e:
        logger.error(f"❌ Ошибка поиска сотрудников: {e}")
        return []