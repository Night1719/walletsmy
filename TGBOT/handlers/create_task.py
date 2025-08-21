from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards import services_keyboard, main_menu_keyboard, cancel_keyboard, duration_keyboard
from storage import get_session
from states import CreateTaskStates
from api_client import create_task, get_user_by_id
from config import ALLOWED_SERVICES, DEFAULT_TYPE_ID, DEFAULT_PRIORITY_ID, DEFAULT_URGENCY_ID, DEFAULT_IMPACT_ID, SERVICE_ID_REMOTE_ACCESS, SERVICE_ID_MISC
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "➕ Создать заявку")
async def start_create_task(message: types.Message, state: FSMContext):
    session = get_session(message.from_user.id)
    if not session:
        await message.answer("Сначала авторизуйтесь: /start")
        return
    await state.set_state(CreateTaskStates.choosing_service)
    await message.answer("Выберите сервис:", reply_markup=services_keyboard())


@router.message(CreateTaskStates.choosing_service, F.text == "⬅️ Назад")
async def cancel_from_service(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Отмена. Возврат в меню.", reply_markup=main_menu_keyboard())


@router.message(CreateTaskStates.choosing_service, F.text)
async def choose_service(message: types.Message, state: FSMContext):
    text = message.text.strip()

    # Разрешены только эти пункты
    allowed_titles = {"Удаленный доступ", "Прочее"}
    if text == "⬅️ Назад":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=main_menu_keyboard())
        return
    if text not in allowed_titles:
        # Игнорируем ввод в этом состоянии, показываем клавиатуру ещё раз
        await message.answer("Выберите один из пунктов ниже:", reply_markup=services_keyboard())
        return

    service_id = None
    # Жестко проставим ServiceId по названию
    if text == "Прочее":
        service_id = SERVICE_ID_MISC
    elif text == "Удаленный доступ":
        service_id = SERVICE_ID_REMOTE_ACCESS

    if not service_id:
        await message.answer("Выберите сервис из списка или нажмите ⬅️ Назад.", reply_markup=services_keyboard())
        return

    await state.update_data(service_id=service_id, service_title=text)
    if text == "Прочее":
        await state.set_state(CreateTaskStates.entering_name)
        await message.answer("Введите название заявки:", reply_markup=cancel_keyboard())
    else:
        # Удаленный доступ: сначала название и описание, затем срок
        await state.update_data(is_remote=True)
        await state.set_state(CreateTaskStates.entering_name)
        await message.answer("Введите название заявки (удаленный доступ):", reply_markup=cancel_keyboard())


@router.message(CreateTaskStates.entering_name, F.text == "❌ Отменить")
async def cancel_from_name(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Отмена. Возврат в меню.", reply_markup=main_menu_keyboard())


@router.message(CreateTaskStates.entering_name, F.text)
async def enter_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("Название не может быть пустым.", reply_markup=cancel_keyboard())
        return
    await state.update_data(name=name)
    await state.set_state(CreateTaskStates.entering_description)
    await message.answer("Введите описание заявки:", reply_markup=cancel_keyboard())


@router.message(CreateTaskStates.entering_description, F.text == "❌ Отменить")
async def cancel_from_desc(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Отмена. Возврат в меню.", reply_markup=main_menu_keyboard())


@router.message(CreateTaskStates.entering_description, F.text)
async def enter_description(message: types.Message, state: FSMContext):
    description = message.text.strip()
    data = await state.get_data()
    session = get_session(message.from_user.id)
    service_title = data.get("service_title")
    is_remote = bool(data.get("is_remote"))

    if service_title == "Прочее" and not is_remote:
        payload = {
            "Name": data.get("name"),
            "Description": description,
            "CreatorId": session["intraservice_id"],
            "ServiceId": SERVICE_ID_MISC,
            "StatusId": 27,  # В работе
        }
        # Дефолты
        if DEFAULT_TYPE_ID:
            payload["TypeId"] = DEFAULT_TYPE_ID
        if DEFAULT_PRIORITY_ID:
            payload["PriorityId"] = DEFAULT_PRIORITY_ID
        if DEFAULT_URGENCY_ID:
            payload["UrgencyId"] = DEFAULT_URGENCY_ID
        if DEFAULT_IMPACT_ID:
            payload["ImpactId"] = DEFAULT_IMPACT_ID

        task_id = create_task(**payload)
        if task_id:
            await message.answer(f"✅ Заявка создана: #{task_id}", reply_markup=main_menu_keyboard())
        else:
            logger.error(f"Create task failed, payload={payload}")
            await message.answer("❌ Не удалось создать заявку. Проверьте обязательные поля (тип/приоритет/срочность/влияние) и ServiceId.", reply_markup=main_menu_keyboard())
        await state.clear()
    else:
        # Удаленный доступ — после описания спрашиваем срок
        await state.update_data(description=description)
        await state.set_state(CreateTaskStates.choosing_remote_duration)
        await message.answer("На сколько дней выдать доступ?", reply_markup=duration_keyboard())


@router.message(CreateTaskStates.choosing_remote_duration, F.text.in_({"1 день", "3 дня", "7 дней", "14 дней"}))
async def choose_remote_duration(message: types.Message, state: FSMContext):
    text = message.text.strip()
    days_map = {"1 день": 1, "3 дня": 3, "7 дней": 7, "14 дней": 14}
    days = days_map.get(text, 1)
    await state.update_data(remote_days=days)
    # Рассчитаем даты: начало сегодня 09:00, окончание через N дней 18:00
    from datetime import datetime, timedelta
    now = datetime.now()
    start = now.replace(hour=9, minute=0, second=0, microsecond=0)
    end = (start + timedelta(days=days)).replace(hour=18, minute=0, second=0, microsecond=0)
    await state.update_data(remote_start=start.strftime("%Y-%m-%d"), remote_end=end.strftime("%Y-%m-%d"))
    # Переходим сразу к созданию
    await enter_remote_end(message, state)


@router.message(CreateTaskStates.entering_remote_end, F.text)
async def enter_remote_end(message: types.Message, state: FSMContext):
    end_date = (await state.get_data()).get("remote_end")
    data = await state.get_data()
    session = get_session(message.from_user.id)
    # Собираем payload для удаленного доступа
    payload = {
        "Name": data.get("name") or f"Удаленный доступ ({session.get('name','')})",
        "Description": data.get("description") or "Оформление удаленного доступа",
        "CreatorId": session["intraservice_id"],
        "ServiceId": SERVICE_ID_REMOTE_ACCESS,
        "StatusId": 36,  # Согласование
        # Поля формы:
        "Field1075": data.get("remote_start"),  # дата начала
        "Field1076": end_date,                   # дата окончания
        "Field1077": 262,                        # константа
    }
    # Дублируем значения в Attributes (на случай другой схемы API)
    payload["Attributes"] = [
        {"Id": 1075, "Value": data.get("remote_start")},
        {"Id": 1076, "Value": end_date},
        {"Id": 1077, "Value": 262},
    ]

    # Попробуем добавить согласующего — непосредственного руководителя пользователя
    try:
        me = get_user_by_id(int(session["intraservice_id"])) or {}
        potential_keys = (
            "ManagerId", "LeaderId", "ChiefId", "BossId", "HeadId",
        )
        manager_id = None
        for key in potential_keys:
            mid = me.get(key)
            if isinstance(mid, int) and mid > 0:
                manager_id = mid
                break
        # иногда менеджер приходит вложенным объектом
        if manager_id is None:
            for key in ("Manager", "Leader", "Chief", "Boss", "Head"):
                obj = me.get(key)
                if isinstance(obj, dict):
                    mid = obj.get("Id")
                    if isinstance(mid, int) and mid > 0:
                        manager_id = mid
                        break
        if manager_id:
            payload["CoordinatorIds"] = str(manager_id)
            payload["CoordinatorId"] = manager_id
    except Exception:
        logger.exception("Не удалось определить руководителя для согласования")
    # Дефолты
    if DEFAULT_TYPE_ID:
        payload["TypeId"] = DEFAULT_TYPE_ID
    if DEFAULT_PRIORITY_ID:
        payload["PriorityId"] = DEFAULT_PRIORITY_ID
    if DEFAULT_URGENCY_ID:
        payload["UrgencyId"] = DEFAULT_URGENCY_ID
    if DEFAULT_IMPACT_ID:
        payload["ImpactId"] = DEFAULT_IMPACT_ID

    task_id = create_task(**payload)
    if task_id:
        await message.answer(f"✅ Заявка создана: #{task_id}", reply_markup=main_menu_keyboard())
    else:
        logger.error(f"Create remote access task failed, payload={payload}")
        await message.answer("❌ Не удалось создать заявку на удаленный доступ. Проверьте обязательные поля.", reply_markup=main_menu_keyboard())
    await state.clear()