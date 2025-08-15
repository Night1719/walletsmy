from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards import services_keyboard, main_menu_keyboard, cancel_keyboard
from storage import get_session
from states import CreateTaskStates
from api_client import create_task
from config import ALLOWED_SERVICES, DEFAULT_TYPE_ID, DEFAULT_PRIORITY_ID, DEFAULT_URGENCY_ID, DEFAULT_IMPACT_ID
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


@router.message(CreateTaskStates.choosing_service, F.text == "❌ Отменить")
async def cancel_from_service(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Отмена. Возврат в меню.", reply_markup=main_menu_keyboard())


@router.message(CreateTaskStates.choosing_service, F.text)
async def choose_service(message: types.Message, state: FSMContext):
    text = message.text.strip()

    service_id = None
    for sid, name in ALLOWED_SERVICES.items():
        if name == text:
            service_id = sid
            break

    if not service_id:
        await message.answer("Выберите сервис из списка или нажмите ❌ Отменить.", reply_markup=services_keyboard())
        return

    await state.update_data(service_id=service_id)
    await state.set_state(CreateTaskStates.entering_name)
    await message.answer("Введите название заявки:", reply_markup=cancel_keyboard())


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

    payload = {
        "Name": data.get("name"),
        "Description": description,
        "CreatorId": session["intraservice_id"],
        "ServiceId": data.get("service_id"),
        "StatusId": 27,
    }

    # Проставим дефолты, если требуются системой
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