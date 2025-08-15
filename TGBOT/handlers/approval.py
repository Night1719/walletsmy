from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from api_client import get_tasks_awaiting_approval, approve_task
from keyboards import approval_actions_inline, link_to_task_inline
from storage import get_session
from states import DeclineStates
from config import HELPDESK_WEB_BASE

router = Router()


@router.message(F.text == "✅ Согласование")
async def list_approvals(message: types.Message, state: FSMContext):
    session = get_session(message.from_user.id)
    if not session:
        await message.answer("Сначала авторизуйтесь: /start")
        return

    tasks = get_tasks_awaiting_approval(session["intraservice_id"])
    if not tasks:
        await message.answer("Нет заявок, ожидающих вашего согласования.")
        return

    for t in tasks[:30]:
        task_id = t.get("Id")
        name = t.get("Name", "Без названия")
        creator_name = t.get("CreatorName", "?")
        due = t.get("PlanEndDate", "")
        desc = (t.get("Description") or "").strip()
        if len(desc) > 300:
            desc = desc[:300] + "…"

        txt = (
            f"📝 Заявка #{task_id}\n"
            f"🔖 {name}\n"
            f"👤 Заявитель: {creator_name}\n"
            f"🗓 Срок: {due}\n\n"
            f"📄 {desc}"
        )
        await message.answer(txt, reply_markup=approval_actions_inline(task_id))


@router.callback_query(F.data.startswith("approval:"))
async def on_approval_action(call: types.CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    if len(parts) < 3:
        await call.answer()
        return

    _, action, task_id_str = parts
    task_id = int(task_id_str)

    # Определяем текущего согласующего как Telegram-пользователя, соответствующего IntraService Id из сессии
    session = get_session(call.from_user.id)
    coordinator_id = session.get("intraservice_id") if session else None
    user_name = (session.get("name") if session else None)

    if action == "ok":
        ok = approve_task(task_id, approve=True, comment="", user_name=user_name, coordinator_id=coordinator_id, set_status_on_success=45)
        if ok:
            try:
                await call.message.edit_reply_markup()
            except Exception:
                pass
            await call.message.answer(f"✅ Заявка #{task_id} согласована.", reply_markup=link_to_task_inline(task_id, HELPDESK_WEB_BASE))
        else:
            await call.message.answer("❌ Не удалось согласовать заявку.")
        await call.answer()
    elif action == "decline":
        await state.set_state(DeclineStates.entering_reason)
        await state.update_data(task_id=task_id)
        await call.message.answer("Укажите причину отклонения:")
        await call.answer()


@router.message(DeclineStates.entering_reason, F.text)
async def on_decline_reason(message: types.Message, state: FSMContext):
    data = await state.get_data()
    task_id = data.get("task_id")
    reason = message.text.strip()
    session = get_session(message.from_user.id)
    coordinator_id = session.get("intraservice_id") if session else None
    user_name = (session.get("name") if session else None)

    if not task_id:
        await message.answer("Не выбрана заявка.")
        await state.clear()
        return

    ok = approve_task(task_id, approve=False, comment=reason or "Отклонено через Telegram", user_name=user_name, coordinator_id=coordinator_id)
    if ok:
        await message.answer(f"❌ Заявка #{task_id} отклонена.")
    else:
        await message.answer("Не удалось отклонить заявку.")
    await state.clear()