import asyncio
import logging
import time
from typing import Dict, Any, List, Tuple
from aiogram import Bot
from config import BACKGROUND_POLL_INTERVAL_SEC, HELPDESK_WEB_BASE
from storage import (
    get_all_sessions,
    get_preferences,
    get_task_cache,
    set_task_cache,
)
from api_client import (
    get_user_tasks_by_creator,
    get_user_tasks,
    get_task_details,
    get_tasks_awaiting_approval,
    get_task_comments,
    get_task_lifetime_comments,
    get_user_by_id,
)
from keyboards import reply_to_task_inline, approval_actions_inline, link_to_task_inline
from metrics import inc_notification, inc_api_error, observe_cycle, set_sessions

logger = logging.getLogger(__name__)

_user_name_cache: dict[int, str] = {}

def _resolve_user_name(user_id: int | str | None) -> str | None:
    if user_id is None:
        return None
    try:
        uid = int(user_id)
    except Exception:
        return None
    if uid in _user_name_cache:
        return _user_name_cache[uid]
    user = get_user_by_id(uid)
    if isinstance(user, dict):
        name = user.get("Name") or user.get("FullName") or user.get("FIO") or user.get("DisplayName")
        if isinstance(name, str) and name.strip():
            _user_name_cache[uid] = name
            return name
    return None


async def send_safe(bot: Bot, chat_id: int, text: str, reply_markup=None) -> None:
    try:
        await bot.send_message(chat_id, text, reply_markup=reply_markup, disable_web_page_preview=True)
    except Exception:
        logger.exception("Failed to send message")


def _extract_task_core(task: Dict[str, Any]) -> Dict[str, Any]:
    def _as_int(v):
        try:
            if v is None:
                return None
            if isinstance(v, int):
                return v
            if isinstance(v, str) and v.isdigit():
                return int(v)
            return int(v)
        except Exception:
            return None

    return {
        "status_id": _as_int(task.get("StatusId")),
        "status_name": task.get("StatusName"),
        "executor_id": _as_int(task.get("ExecutorId")),
        "executor_name": task.get("ExecutorName"),
        "name": task.get("Name"),
        "create_date": task.get("CreateDate"),
    }


def _truncate(text: str, limit: int = 400) -> str:
    if text is None:
        return ""
    text = text.strip()
    return text if len(text) <= limit else text[:limit] + "…"


def _rotate_indices(length: int, start: int, count: int) -> List[int]:
    if length <= 0 or count <= 0:
        return []
    return [((start + i) % length) for i in range(min(count, length))]


def _extract_comments(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw = data.get("Comments")
    # Comments can be a list or nested object
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in ("Comments", "Items", "TaskComments", "List"):
            val = raw.get(key)
            if isinstance(val, list):
                return val
    # Fallback: search shallow keys
    for key in ("TaskComments", "CommentsList"):
        val = data.get(key)
        if isinstance(val, list):
            return val
    return []


def _comment_id(c: Dict[str, Any]) -> str | None:
    cid = c.get("Id") or c.get("CommentId") or c.get("ID")
    if cid is not None:
        return str(cid)
    # Fallback fingerprint based on timestamp + author + text
    ts = c.get("CreateDate") or c.get("Date") or c.get("Time") or ""
    author = c.get("CreatorName") or c.get("UserName") or c.get("Author") or c.get("AuthorName") or ""
    text = c.get("Text") or c.get("Body") or c.get("CommentText") or c.get("Description") or c.get("Comments") or ""
    fingerprint = f"{ts}|{author}|{text[:64]}"
    return fingerprint if fingerprint.strip() else None


def _comment_author(c: Dict[str, Any]) -> str:
    # Nested structures first
    creator = c.get("Creator")
    if isinstance(creator, dict):
        for k in ("Name", "FullName", "FIO", "DisplayName"):
            v = creator.get(k)
            if isinstance(v, str) and v.strip():
                return v
    user = c.get("User")
    if isinstance(user, dict):
        for k in ("Name", "FullName", "FIO", "DisplayName"):
            v = user.get(k)
            if isinstance(v, str) and v.strip():
                return v
    # Flat fields
    return (
        c.get("CreatorName")
        or c.get("UserName")
        or c.get("AuthorName")
        or c.get("Author")
        or c.get("Creator")
        or c.get("User")
        or _resolve_user_name(c.get("CreatorId") or c.get("UserId") or c.get("AuthorId") or c.get("AddedById"))
        or "Кто-то"
    )


def _comment_text(c: Dict[str, Any]) -> str:
    return c.get("Text") or c.get("Body") or c.get("CommentText") or c.get("Description") or "(без текста)"


def _comment_sort_key(c: Dict[str, Any]):
    # Prefer numeric Id for ordering; fallback to 0
    try:
        return int(c.get("Id") or c.get("CommentId") or 0)
    except Exception:
        return 0


async def _check_new_tasks(
    bot: Bot,
    chat_id: int,
    open_tasks: List[Dict[str, Any]],
    task_cache: Dict[str, Any],
    prefs: Dict[str, Any],
) -> None:
    known_ids = set(task_cache.get("tasks", {}).keys())
    current_ids = {str(t.get("Id")) for t in open_tasks if t.get("Id") is not None}

    if not task_cache.get("initialized"):
        # First run for user: just mark as seen to avoid flood
        task_cache["initialized"] = True
        # Initialize last_comment_ids and mark tasks as known to avoid sending old events
        for t in open_tasks:
            tid = str(t.get("Id"))
            details = get_task_details(int(tid)) or {}
            comments = _extract_comments(details)
            last_ids = [cid for cid in [ _comment_id(c) for c in comments[-50:] ] if cid is not None]
            entry = task_cache.setdefault("tasks", {}).setdefault(tid, {})
            entry["last_comment_ids_str"] = last_ids
            # also seed core to prevent first-cycle status spam
            entry.update(_extract_task_core(t))
        # На первом проходе не отправляем никакие уведомления о новых задачах
        return

    if not prefs.get("notify_new_task"):
        return

    new_ids = [tid for tid in current_ids if tid not in known_ids]
    for tid in new_ids[:20]:
        name = next((t.get("Name") for t in open_tasks if str(t.get("Id")) == tid), "Новая заявка")
        await send_safe(
            bot,
            chat_id,
            f"🆕 Новая заявка #{tid}\n{_truncate(name, 200)}",
            reply_markup=link_to_task_inline(int(tid), HELPDESK_WEB_BASE),
        )
        inc_notification("new_task")


async def _check_status_and_executor(
    bot: Bot,
    chat_id: int,
    open_tasks: List[Dict[str, Any]],
    task_cache: Dict[str, Any],
    prefs: Dict[str, Any],
) -> None:
    cached_tasks: Dict[str, Any] = task_cache.get("tasks", {})

    status_notifies = 0
    max_status_notifies = 5
    for task in open_tasks:
        task_id = str(task.get("Id"))
        core = _extract_task_core(task)
        prev = cached_tasks.get(task_id, {})

        # Status change
        if prefs.get("notify_status") and prev.get("status_id") is not None:
            if core.get("status_id") != prev.get("status_id") and status_notifies < max_status_notifies:
                old_name = prev.get('status_name') or str(prev.get('status_id'))
                new_name = core.get('status_name') or str(core.get('status_id'))
                await send_safe(
                    bot,
                    chat_id,
                    f"🔔 Обновление заявки #{task_id}\n• Статус: {old_name} → {new_name}",
                    reply_markup=link_to_task_inline(int(task_id), HELPDESK_WEB_BASE),
                )
                inc_notification("status")
                status_notifies += 1

        # Executor change
        if prefs.get("notify_executor") and prev.get("executor_id") is not None:
            if core.get("executor_id") != prev.get("executor_id"):
                await send_safe(
                    bot,
                    chat_id,
                    f"🔔 Обновление заявки #{task_id}\n• Исполнитель: {prev.get('executor_name', 'не назначен')} → {core.get('executor_name', 'не назначен')}",
                    reply_markup=link_to_task_inline(int(task_id), HELPDESK_WEB_BASE),
                )
                inc_notification("executor")

        # Save current core
        cached_entry = cached_tasks.get(task_id, {})
        cached_entry.update(core)
        cached_tasks[task_id] = cached_entry

    # Detect tasks that left open set (potentially done)
    current_ids = {str(t.get("Id")) for t in open_tasks}
    previously_open_ids = set(cached_tasks.keys())
    closed_now = list(previously_open_ids - current_ids)

    if prefs.get("notify_done"):
        # Check a limited number per cycle to avoid burst calls
        for task_id in closed_now[:10]:
            try:
                details = get_task_details(int(task_id))
                status_name = (details or {}).get("StatusName", "завершена")
                await send_safe(
                    bot,
                    chat_id,
                    f"✅ Заявка #{task_id} перешла в статус: {status_name}",
                    reply_markup=link_to_task_inline(int(task_id), HELPDESK_WEB_BASE),
                )
                inc_notification("done")
            except Exception:
                logger.exception("Failed to notify done for task %s", task_id)
                inc_api_error("notify_done")
            finally:
                # Remove from cache to keep it clean
                cached_tasks.pop(task_id, None)

    # Remove any remaining tasks that are no longer open from cache core (if not notified)
    for task_id in closed_now[10:]:
        cached_tasks.pop(task_id, None)

    task_cache["tasks"] = cached_tasks


async def _check_comments(
    bot: Bot,
    chat_id: int,
    open_tasks: List[Dict[str, Any]],
    task_cache: Dict[str, Any],
    prefs: Dict[str, Any],
) -> None:
    if not prefs.get("notify_comment"):
        return

    cached_tasks: Dict[str, Any] = task_cache.get("tasks", {})
    rotation = task_cache.setdefault("rotation", {})
    start_index = int(rotation.get("comment_index", 0))

    # Round-robin check a few tasks each cycle (wider window)
    indices = _rotate_indices(len(open_tasks), start_index, count=10)
    rotation["comment_index"] = (start_index + len(indices)) % max(1, len(open_tasks))

    for idx in indices:
        t = open_tasks[idx]
        task_id = str(t.get("Id"))
        try:
            details = get_task_details(int(task_id)) or {}
            comments = _extract_comments(details)
            if not comments:
                # пробуем прямой эндпоинт
                comments = get_task_comments(int(task_id)) or []
            if not comments:
                # пробуем tasklifetime
                lifetimes = get_task_lifetime_comments(int(task_id)) or []
                # вытаскиваем только пользовательские комментарии
                comments = []
                for e in lifetimes:
                    text = (e.get("Comments") or e.get("Comment") or "").strip()
                    is_operator = bool(e.get("AuthorIsOperator"))
                    if text and not is_operator:
                        comments.append({
                            "Id": e.get("Id") or e.get("CommentId") or 0,
                            "CreatorName": e.get("Author") or e.get("AuthorName") or "",
                            "Text": text,
                            "CreateDate": e.get("CreateDate") or e.get("Date") or e.get("Time") or "",
                        })
            total = len(comments)
            if not isinstance(comments, list):
                continue

            # Если задача видится впервые после инициализации — считаем текущие комментарии базовой линией
            if task_id not in cached_tasks and task_cache.get("initialized"):
                last_ids_seed = [cid for cid in [_comment_id(c) for c in comments[-50:]] if cid is not None]
                cached_tasks[task_id] = {"last_comment_ids_str": last_ids_seed}
                continue

            entry = cached_tasks.setdefault(task_id, {})
            prev_ids: List[str] = entry.get("last_comment_ids_str", [])
            # Если база не инициализирована для этой задачи — зафиксируем текущие и пропустим
            if not prev_ids:
                last_seed = [cid for cid in [_comment_id(c) for c in comments[-50:]] if cid is not None]
                entry["last_comment_ids_str"] = last_seed
                continue

            new_comments = [c for c in comments if (_comment_id(c) not in prev_ids)]
            new_count = len(new_comments)
            if new_count:
                logger.info(f"🛈 Комментарии #{task_id}: всего={total}, новых={new_count}")
                # Sort and show last three, newest at bottom
                new_comments.sort(key=_comment_sort_key)
                to_show = new_comments[-3:]
                for c in to_show:
                    author = _comment_author(c)
                    text = _truncate(_comment_text(c))
                    await send_safe(
                        bot,
                        chat_id,
                        f"💬 Новый комментарий в заявке #{task_id}\n— {author}: {text}",
                        reply_markup=reply_to_task_inline(int(task_id)),
                    )
                    inc_notification("comment")

            # Always refresh last seen ids to prevent repeat sends on next cycles
            last_ids = [cid for cid in [_comment_id(c) for c in comments[-50:]] if cid is not None]
            entry = cached_tasks.setdefault(task_id, {})
            entry["last_comment_ids_str"] = last_ids
        except Exception:
            logger.exception("Failed to check comments for task %s", task_id)
            inc_api_error("check_comments")

    task_cache["tasks"] = cached_tasks
    task_cache["rotation"] = rotation


async def _check_approvals(
    bot: Bot,
    chat_id: int,
    intraservice_id: int,
    task_cache: Dict[str, Any],
    prefs: Dict[str, Any],
) -> None:
    if not prefs.get("notify_approval"):
        return

    try:
        tasks = get_tasks_awaiting_approval(intraservice_id)
    except Exception:
        logger.exception("Failed to fetch approvals for %s", intraservice_id)
        inc_api_error("approvals_fetch")
        return

    cached_approvals: List[int] = task_cache.get("approvals", [])
    current_ids = [t.get("Id") for t in tasks if t.get("Id") is not None]

    # На первом запуске инициализируем и не шлем исторические согласования
    if not task_cache.get("initialized"):
        task_cache["approvals"] = current_ids
        return

    # New tasks awaiting approval
    new_ids = [tid for tid in current_ids if tid not in cached_approvals]
    for tid in new_ids[:30]:
        try:
            name = next((t.get("Name") for t in tasks if t.get("Id") == tid), None) or "Заявка"
            await send_safe(
                bot,
                chat_id,
                f"🟨 Требуется ваше согласование\n#{tid}: {name}",
                reply_markup=approval_actions_inline(tid),
            )
            inc_notification("approval")
        except Exception:
            logger.exception("Failed to notify approval for task %s", tid)
            inc_api_error("notify_approval")

    # Update cache
    task_cache["approvals"] = current_ids


async def run_user_checks(bot: Bot, chat_id: int) -> None:
    sessions: Dict[str, Dict[str, Any]] = get_all_sessions()
    session = sessions.get(str(chat_id))
    if not session:
        return
    intraservice_id = session.get("intraservice_id")
    if not intraservice_id:
        return

    prefs = get_preferences(chat_id)
    cache = get_task_cache(chat_id)

    # Уведомления по статусам/новым заявкам — только по созданным пользователем
    open_tasks = get_user_tasks_by_creator(intraservice_id, "open") or []
    logger.info(f"🛈 User {chat_id}: open_tasks_by_creator={len(open_tasks)}")

    # Уведомления о комментариях — по всем ролям пользователя
    open_tasks_for_comments = get_user_tasks(intraservice_id, "open") or open_tasks

    await _check_new_tasks(bot, chat_id, open_tasks, cache, prefs)
    await _check_status_and_executor(bot, chat_id, open_tasks, cache, prefs)
    await _check_comments(bot, chat_id, open_tasks_for_comments, cache, prefs)
    await _check_approvals(bot, chat_id, intraservice_id, cache, prefs)

    set_task_cache(chat_id, cache)


async def background_worker(bot: Bot):
    while True:
        start = time.perf_counter()
        try:
            sessions: Dict[str, Dict[str, Any]] = get_all_sessions()
            set_sessions(len(sessions))
            for chat_id_str, session in sessions.items():
                try:
                    chat_id = int(chat_id_str)
                    await run_user_checks(bot, chat_id)
                    # маленькая пауза между пользователями, чтобы не забивать петлю
                    await asyncio.sleep(0.05)
                except Exception:
                    logger.exception("background loop error for user %s", chat_id_str)
                    inc_api_error("user_loop")

            await asyncio.sleep(BACKGROUND_POLL_INTERVAL_SEC)
        except Exception as e:
            logger.exception("Background error: %s", e)
            inc_api_error("background")
            await asyncio.sleep(10)
        finally:
            observe_cycle(time.perf_counter() - start)