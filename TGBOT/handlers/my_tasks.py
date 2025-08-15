from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from api_client import get_user_tasks, get_task_details, add_comment_to_task
from keyboards import my_tasks_menu_keyboard, task_actions_inline, link_to_task_inline
from storage import get_session
from states import CommentStates
from config import HELPDESK_WEB_BASE

router = Router()


def _status_name_from(task: dict) -> str:
    return (
        task.get("StatusName")
        or task.get("Status")
        or task.get("StatusDisplay")
        or "?"
    )


@router.message(F.text.in_({"Открытые", "Завершённые", "⬅️ Назад"}))
async def my_tasks_menu(message: types.Message, state: FSMContext):
    text = message.text.strip()
    session = get_session(message.from_user.id)
    if not session:
        await message.answer("Сначала авторизуйтесь: /start")
        return

    if text == "⬅️ Назад":
        await message.answer("Возврат в главное меню. /menu")
        return

    status = "open" if text == "Открытые" else "closed"
    tasks = get_user_tasks(session["intraservice_id"], status)
    if not tasks:
        await message.answer("Заявок не найдено.")
        return

    for t in tasks[:30]:
        task_id = t.get("Id")
        name = t.get("Name", "Без названия")
        status_name = _status_name_from(t)
        creator_date = t.get("CreateDate", "")
        description = (t.get("Description") or "").strip()
        if len(description) > 300:
            description = description[:300] + "…"

        text_msg = (
            f"📋 Заявка #{task_id}\n"
            f"🔖 Название: {name}\n"
            f"📊 Статус: {status_name}\n"
            f"📅 Создана: {creator_date}\n"
            f"📄 Описание: {description}"
        )
        await message.answer(text_msg, reply_markup=task_actions_inline(task_id))

    await message.answer("🔚 Конец списка.", reply_markup=my_tasks_menu_keyboard())


@router.callback_query(F.data.startswith("task:"))
async def on_task_inline(call: types.CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    if len(parts) < 3:
        await call.answer()
        return

    action, action2, task_id_str = parts
    task_id = int(task_id_str)

    if action == "task" and action2 == "details":
        data = get_task_details(task_id)
        if not data:
            await call.answer("Не удалось получить детали", show_alert=True)
            return
        name = data.get("Name", "Без названия")
        status_name = _status_name_from(data)
        description = data.get("Description", "")
        comments = data.get("Comments", [])
        comments_text = "\n".join([f"— {c.get('CreatorName')}: {c.get('Text')}" for c in comments[-5:]]) or "Комментариев нет"
        text_msg = (
            f"📋 Заявка #{task_id}\n"
            f"🔖 {name}\n"
            f"📊 {status_name}\n\n"
            f"📄 {description}\n\n"
            f"💬 Комментарии (последние):\n{comments_text}"
        )
        await call.message.answer(text_msg, reply_markup=link_to_task_inline(task_id, HELPDESK_WEB_BASE))
        await call.answer()
    elif action == "task" and action2 == "comment":
        await state.set_state(CommentStates.entering_comment)
        await state.update_data(task_id=task_id)
        await call.message.answer("Введите текст комментария:")
        await call.answer()


@router.message(CommentStates.entering_comment, F.text)
async def on_comment_entered(message: types.Message, state: FSMContext):
    data = await state.get_data()
    task_id = data.get("task_id")
    if not task_id:
        await message.answer("Заявка не выбрана.")
        await state.clear()
        return
    text = message.text.strip()
    if not text:
        await message.answer("Пустой комментарий. Отменено.")
        await state.clear()
        return

    ok = add_comment_to_task(task_id, text, public=True)
    if ok:
        await message.answer("✅ Комментарий добавлен.")
    else:
        await message.answer("❌ Не удалось добавить комментарий.")
    await state.clear()