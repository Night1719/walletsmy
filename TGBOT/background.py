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
    get_user_tasks,
    get_task_details,
    get_tasks_awaiting_approval,
    get_task_comments,
)
from keyboards import link_to_task_inline, approval_actions_inline
from metrics import inc_notification, inc_api_error, observe_cycle, set_sessions

logger = logging.getLogger(__name__)


async def send_safe(bot: Bot, chat_id: int, text: str, reply_markup=None) -> None:
    try:
        await bot.send_message(chat_id, text, reply_markup=reply_markup, disable_web_page_preview=True)
    except Exception:
        logger.exception("Failed to send message")


def _extract_task_core(task: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status_id": task.get("StatusId"),
        "status_name": task.get("StatusName"),
        "executor_id": task.get("ExecutorId"),
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
    return str(cid) if cid is not None else None


def _comment_author(c: Dict[str, Any]) -> str:
    return c.get("CreatorName") or c.get("UserName") or c.get("AuthorName") or c.get("Creator") or "Кто-то"


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
    if not prefs.get("notify_new_task"):
        return
    known_ids = set(task_cache.get("tasks", {}).keys())
    current_ids = {str(t.get("Id")) for t in open_tasks if t.get("Id") is not None}

    if not task_cache.get("initialized"):
        # First run for user: just mark as seen to avoid flood
        task_cache["initialized"] = True
        # Initialize last_comment_ids to avoid sending old comments as new
        for t in open_tasks:
            tid = str(t.get("Id"))
            details = get_task_details(int(tid)) or {}
            comments = _extract_comments(details)
            last_ids = [cid for cid in [ _comment_id(c) for c in comments[-50:] ] if cid is not None]
            entry = task_cache.setdefault("tasks", {}).setdefault(tid, {})
            entry["last_comment_ids_str"] = last_ids
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

    for task in open_tasks:
        task_id = str(task.get("Id"))
        core = _extract_task_core(task)
        prev = cached_tasks.get(task_id, {})

        # Status change
        if prefs.get("notify_status") and prev.get("status_id") is not None:
            if core.get("status_id") != prev.get("status_id"):
                old_name = prev.get('status_name') or str(prev.get('status_id'))
                new_name = core.get('status_name') or str(core.get('status_id'))
                await send_safe(
                    bot,
                    chat_id,
                    f"🔔 Обновление заявки #{task_id}\n• Статус: {old_name} → {new_name}",
                    reply_markup=link_to_task_inline(int(task_id), HELPDESK_WEB_BASE),
                )
                inc_notification("status")

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
                comments = get_task_comments(int(task_id)) or []
            total = len(comments)
            if not isinstance(comments, list):
                continue

            prev_ids: List[str] = cached_tasks.get(task_id, {}).get("last_comment_ids_str", [])
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
                        reply_markup=link_to_task_inline(int(task_id), HELPDESK_WEB_BASE),
                    )
                    inc_notification("comment")

                # Keep last up to 50 ids from all comments
                last_ids = [cid for cid in [ _comment_id(c) for c in comments[-50:] ] if cid is not None]
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

    open_tasks = get_user_tasks(intraservice_id, "open") or []
    logger.info(f"🛈 User {chat_id}: open_tasks={len(open_tasks)}")

    await _check_new_tasks(bot, chat_id, open_tasks, cache, prefs)
    await _check_status_and_executor(bot, chat_id, open_tasks, cache, prefs)
    await _check_comments(bot, chat_id, open_tasks, cache, prefs)
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