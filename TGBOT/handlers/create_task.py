from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards import services_keyboard, main_menu_keyboard
from storage import get_session
from states import CreateTaskStates
from api_client import create_task
from config import ALLOWED_SERVICES

router = Router()


@router.message(F.text == "➕ Создать заявку")
async def start_create_task(message: types.Message, state: FSMContext):
    session = get_session(message.from_user.id)
    if not session:
        await message.answer("Сначала авторизуйтесь: /start")
        return
    await state.set_state(CreateTaskStates.choosing_service)
    await message.answer("Выберите сервис:", reply_markup=services_keyboard())


@router.message(CreateTaskStates.choosing_service, F.text)
async def choose_service(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if text == "⬅️ Назад":
        await state.clear()
        await message.answer("Отмена. Возврат в меню.", reply_markup=main_menu_keyboard())
        return

    service_id = None
    for sid, name in ALLOWED_SERVICES.items():
        if name == text:
            service_id = sid
            break

    if not service_id:
        await message.answer("Выберите сервис из списка.")
        return

    await state.update_data(service_id=service_id)
    await state.set_state(CreateTaskStates.entering_name)
    await message.answer("Введите название заявки:")


@router.message(CreateTaskStates.entering_name, F.text)
async def enter_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("Название не может быть пустым.")
        return
    await state.update_data(name=name)
    await state.set_state(CreateTaskStates.entering_description)
    await message.answer("Введите описание заявки:")


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

    task_id = create_task(**payload)
    if task_id:
        await message.answer(f"✅ Заявка создана: #{task_id}")
    else:
        await message.answer("❌ Не удалось создать заявку.")
    await state.clear()