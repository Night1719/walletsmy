import json
import os
from typing import Any, Dict, Optional
from config import USER_DATA_FILE, USER_PREFERENCES_FILE, TASK_CACHE_FILE


def _ensure_file(path: str) -> None:
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("{}")


def _read_json(path: str) -> Dict[str, Any]:
    _ensure_file(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}


def _write_json(path: str, data: Dict[str, Any]) -> None:
    _ensure_file(path)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


# === Sessions (authorized users) ===

def get_all_sessions() -> Dict[str, Dict[str, Any]]:
    return _read_json(USER_DATA_FILE)


def set_session(telegram_user_id: int, session: Dict[str, Any]) -> None:
    data = get_all_sessions()
    data[str(telegram_user_id)] = session
    _write_json(USER_DATA_FILE, data)


def get_session(telegram_user_id: int) -> Optional[Dict[str, Any]]:
    return get_all_sessions().get(str(telegram_user_id))


# === Preferences ===

_DEFAULT_PREFS = {
    "notify_comment": True,
    "notify_status": True,
    "notify_executor": True,
    "notify_done": True,
    "notify_approval": True,
}


def get_all_preferences() -> Dict[str, Dict[str, Any]]:
    return _read_json(USER_PREFERENCES_FILE)


def get_preferences(telegram_user_id: int) -> Dict[str, Any]:
    all_prefs = get_all_preferences()
    prefs = all_prefs.get(str(telegram_user_id), {}).copy()
    for key, val in _DEFAULT_PREFS.items():
        prefs.setdefault(key, val)
    return prefs


def set_preferences(telegram_user_id: int, preferences: Dict[str, Any]) -> None:
    all_prefs = get_all_preferences()
    merged = get_preferences(telegram_user_id)
    merged.update(preferences)
    all_prefs[str(telegram_user_id)] = merged
    _write_json(USER_PREFERENCES_FILE, all_prefs)


# === Task cache for background notifications ===

def get_all_task_cache() -> Dict[str, Any]:
    return _read_json(TASK_CACHE_FILE)


def get_task_cache(telegram_user_id: int) -> Dict[str, Any]:
    cache = get_all_task_cache().get(str(telegram_user_id), {})
    cache.setdefault("approvals", [])
    cache.setdefault("tasks", {})
    return cache


def set_task_cache(telegram_user_id: int, cache: Dict[str, Any]) -> None:
    all_cache = get_all_task_cache()
    all_cache[str(telegram_user_id)] = cache
    _write_json(TASK_CACHE_FILE, all_cache)