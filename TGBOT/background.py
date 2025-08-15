import asyncio
import logging
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
)
from keyboards import link_to_task_inline, approval_actions_inline

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
                await send_safe(
                    bot,
                    chat_id,
                    f"🔔 Обновление заявки #{task_id}\n• Статус: {prev.get('status_name', '?')} → {core.get('status_name', '?')}",
                    reply_markup=link_to_task_inline(int(task_id), HELPDESK_WEB_BASE),
                )

        # Executor change
        if prefs.get("notify_executor") and prev.get("executor_id") is not None:
            if core.get("executor_id") != prev.get("executor_id"):
                await send_safe(
                    bot,
                    chat_id,
                    f"🔔 Обновление заявки #{task_id}\n• Исполнитель: {prev.get('executor_name', 'не назначен')} → {core.get('executor_name', 'не назначен')}",
                    reply_markup=link_to_task_inline(int(task_id), HELPDESK_WEB_BASE),
                )

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
            except Exception:
                logger.exception("Failed to notify done for task %s", task_id)
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

    # Round-robin check a few tasks each cycle
    indices = _rotate_indices(len(open_tasks), start_index, count=3)
    rotation["comment_index"] = (start_index + len(indices)) % max(1, len(open_tasks))

    for idx in indices:
        t = open_tasks[idx]
        task_id = str(t.get("Id"))
        try:
            details = get_task_details(int(task_id))
            if not details:
                continue
            comments = details.get("Comments", [])
            if not isinstance(comments, list):
                continue

            # Determine new comments by Id
            prev_ids: List[int] = cached_tasks.get(task_id, {}).get("last_comment_ids", [])
            new_comments = [c for c in comments if c.get("Id") not in prev_ids]
            # Only notify for actually new ones; update cache with the last few ids
            if new_comments:
                # Notify only for the most recent few to avoid spam
                for c in new_comments[-3:]:
                    author = c.get("CreatorName") or "Кто-то"
                    text = _truncate(c.get("Text") or "")
                    await send_safe(
                        bot,
                        chat_id,
                        f"💬 Новый комментарий в заявке #{task_id}\n— {author}: {text}",
                        reply_markup=link_to_task_inline(int(task_id), HELPDESK_WEB_BASE),
                    )

                # Keep last up to 20 comment ids
                last_ids = [c.get("Id") for c in comments[-20:] if c.get("Id") is not None]
                entry = cached_tasks.setdefault(task_id, {})
                entry["last_comment_ids"] = last_ids
        except Exception:
            logger.exception("Failed to check comments for task %s", task_id)

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
        except Exception:
            logger.exception("Failed to notify approval for task %s", tid)

    # Update cache
    task_cache["approvals"] = current_ids


async def background_worker(bot: Bot):
    while True:
        try:
            sessions: Dict[str, Dict[str, Any]] = get_all_sessions()
            for chat_id_str, session in sessions.items():
                try:
                    chat_id = int(chat_id_str)
                    intraservice_id = session.get("intraservice_id")
                    if not intraservice_id:
                        continue

                    prefs = get_preferences(chat_id)
                    cache = get_task_cache(chat_id)

                    # Fetch current open tasks
                    open_tasks = get_user_tasks(intraservice_id, "open") or []

                    await _check_status_and_executor(bot, chat_id, open_tasks, cache, prefs)
                    await _check_comments(bot, chat_id, open_tasks, cache, prefs)
                    await _check_approvals(bot, chat_id, intraservice_id, cache, prefs)

                    set_task_cache(chat_id, cache)
                except Exception:
                    logger.exception("background loop error for user %s", chat_id_str)

            await asyncio.sleep(BACKGROUND_POLL_INTERVAL_SEC)
        except Exception as e:
            logger.exception("Background error: %s", e)
            await asyncio.sleep(10)