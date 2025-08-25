from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from api_client import get_tasks_awaiting_approval, approve_task, get_task_details, get_task_comments, get_task_lifetime_comments
from keyboards import approval_actions_inline, link_to_task_inline, approval_detail_keyboard
from storage import get_session
from states import DeclineStates
from config import HELPDESK_WEB_BASE
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def format_date(date_str: str) -> str:
    """
    Форматирует дату в формат дд-мм-гггг чч:мм
    Поддерживает различные форматы входных дат
    """
    if not date_str:
        return "дата не указана"
    
    try:
        # Пробуем различные форматы дат
        date_formats = [
            "%Y-%m-%dT%H:%M:%S.%f",  # 2025-08-25T10:50:55.834402
            "%Y-%m-%dT%H:%M:%S",     # 2025-08-25T10:50:55
            "%Y-%m-%d %H:%M:%S",     # 2025-08-25 10:50:55
            "%d.%m.%Y %H:%M:%S",     # 25.08.2025 10:50:55
            "%d.%m.%Y %H:%M",        # 25.08.2025 10:50
            "%Y-%m-%d",              # 2025-08-25
            "%d.%m.%Y",              # 25.08.2025
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%d-%m-%Y %H:%M")
            except ValueError:
                continue
        
        # Если не удалось распарсить, возвращаем как есть
        return date_str
        
    except Exception:
        return date_str

router = Router()


async def show_task_approval_details(message: types.Message, task_id: int):
    """Показать детальную информацию о заявке на согласование"""
    try:
        # Получаем детали заявки
        task_details = get_task_details(task_id) or {}
        
        # Получаем информацию об авторе
        creator_id = task_details.get("CreatorId")
        creator_name = task_details.get("CreatorName") or task_details.get("Creator") or "Неизвестно"
        creator_title = task_details.get("CreatorTitle") or task_details.get("CreatorPosition") or "Не указано"
        
        # Получаем описание заявки
        description = task_details.get("Description") or "Описание не указано"
        if len(description) > 500:
            description = description[:500] + "…"
        
        # Получаем последние комментарии
        comments = get_task_comments(task_id) or []
        logger.info(f"ℹ️ Заявка #{task_id}: Получено {len(comments)} комментариев через get_task_comments")
        
        # Логируем структуру первого комментария для отладки
        if comments:
            logger.info(f"ℹ️ Заявка #{task_id}: Структура первого комментария: {comments[0]}")
            # Логируем все доступные поля
            logger.info(f"ℹ️ Заявка #{task_id}: Все поля комментария: {list(comments[0].keys())}")
        
        # Нормализуем структуру комментариев из get_task_comments
        normalized_comments = []
        for comment in comments:
            text = (comment.get("Comments") or comment.get("Comment") or comment.get("Text") or "").strip()
            if text:
                date = comment.get("CreateDate") or comment.get("Date") or comment.get("CreateTime") or comment.get("Time") or ""
                normalized_comments.append({
                    "Text": text,
                    "CreateDate": date
                })
                logger.debug(f"ℹ️ Заявка #{task_id}: Комментарий ({date}): {text[:50]}...")
        
        if not normalized_comments:
            # Пробуем получить через lifetime
            lifetime_comments = get_task_lifetime_comments(task_id) or []
            logger.info(f"ℹ️ Заявка #{task_id}: Получено {len(lifetime_comments)} комментариев через lifetime")
            
            # Логируем структуру первого lifetime комментария для отладки
            if lifetime_comments:
                logger.info(f"ℹ️ Заявка #{task_id}: Структура первого lifetime комментария: {lifetime_comments[0]}")
                # Логируем все доступные поля
                logger.info(f"ℹ️ Заявка #{task_id}: Все поля lifetime комментария: {list(lifetime_comments[0].keys())}")
            
            # Фильтруем только пользовательские комментарии
            for comment in lifetime_comments:
                text = (comment.get("Comments") or comment.get("Comment") or "").strip()
                is_operator = comment.get("AuthorIsOperator", False)
                if text and not is_operator:
                    date = comment.get("CreateDate") or comment.get("Date") or comment.get("CreateTime") or ""
                    normalized_comments.append({
                        "Text": text,
                        "CreateDate": date
                    })
                    logger.debug(f"ℹ️ Заявка #{task_id}: Lifetime комментарий ({date}): {text[:50]}...")
        
        # Берем последние 3 комментария
        recent_comments = normalized_comments[-3:] if normalized_comments else []
        logger.info(f"ℹ️ Заявка #{task_id}: Итого {len(normalized_comments)} комментариев, показываем последние {len(recent_comments)}")
        
        # Формируем сообщение
        message_text = f"""📋 Заявка #{task_id} на согласование

👤 Автор: {creator_name}
💼 Должность: {creator_title}

📄 Описание:
{description}

💬 Последние комментарии:"""
        
        if recent_comments:
            for i, comment in enumerate(recent_comments, 1):
                text = comment.get("Text", "").strip()
                date_str = comment.get("CreateDate", "")
                
                # Форматируем дату в формат дд-мм-гггг чч:мм
                formatted_date = format_date(date_str)
                
                if len(text) > 200:
                    text = text[:200] + "…"
                
                message_text += f"\n\n{i}. ({formatted_date}):\n{text}"
        else:
            message_text += "\n\nКомментариев пока нет"
        
        # Отправляем сообщение с кнопками для согласования
        await message.answer(message_text, reply_markup=approval_detail_keyboard(task_id))
        
    except Exception as e:
        logger.error(f"Ошибка при получении деталей заявки {task_id}: {e}")
        await message.answer(f"❌ Не удалось загрузить детали заявки #{task_id}")


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

    await message.answer(f"📋 Найдено {len(tasks)} заявок, ожидающих согласования:")
    
    for t in tasks[:30]:
        task_id = t.get("Id")
        name = t.get("Name", "Без названия")
        creator_name = (
            t.get("CreatorName")
            or t.get("Creator")
            or t.get("CreatorLogin")
            or "?"
        )
        due = (
            t.get("Deadline")
            or t.get("PlanEndDate")
            or t.get("ReactionDate")
            or t.get("ReactionDateFact")
            or t.get("ResolutionDateFact")
            or ""
        )

        # Получаем детальную информацию о заявке
        task_details = get_task_details(task_id) or {}
        creator_title = task_details.get("CreatorTitle") or task_details.get("CreatorPosition") or "Не указано"
        description = task_details.get("Description") or "Описание не указано"
        if len(description) > 300:
            description = description[:300] + "…"

        txt = (
            f"📝 Заявка #{task_id}\n"
            f"🔖 {name}\n"
            f"👤 Заявитель: {creator_name}\n"
            f"💼 Должность: {creator_title}\n"
            f"🗓 Срок: {due}\n\n"
            f"📄 {description}"
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

    if action == "goto":
        # Переходим в меню согласования с детальной информацией
        await show_task_approval_details(call.message, task_id)
        await call.answer()
        return

    # Определяем текущего согласующего как Telegram-пользователя, соответствующего IntraService Id из сессии
    session = get_session(call.from_user.id)
    coordinator_id = session.get("intraservice_id") if session else None
    user_name = (session.get("name") if session else None)

    if action == "ok":
        ok = approve_task(task_id, approve=True, comment="", user_name=user_name, coordinator_id=coordinator_id)
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