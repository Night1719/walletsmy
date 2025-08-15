from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from keyboards import services_keyboard, main_menu_keyboard
from storage import get_session
from states import CreateTaskStates
from api_client import create_task
from config import ALLOWED_SERVICES


async def start_create_task(message: types.Message, state: FSMContext):
    if message.text.strip() != "➕ Создать заявку":
        return
    session = get_session(message.from_user.id)
    if not session:
        await message.answer("Сначала авторизуйтесь: /start")
        return
    await CreateTaskStates.choosing_service.set()
    await message.answer("Выберите сервис:", reply_markup=services_keyboard())


async def choose_service(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if text == "⬅️ Назад":
        await state.finish()
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
    await CreateTaskStates.entering_name.set()
    await message.answer("Введите название заявки:")


async def enter_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("Название не может быть пустым.")
        return
    await state.update_data(name=name)
    await CreateTaskStates.entering_description.set()
    await message.answer("Введите описание заявки:")


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
    await state.finish()


def register_create_task_handlers(dp: Dispatcher):
    dp.register_message_handler(start_create_task, lambda m: m.text and m.text.strip() == "➕ Создать заявку", state="*")
    dp.register_message_handler(choose_service, state=CreateTaskStates.choosing_service)
    dp.register_message_handler(enter_name, state=CreateTaskStates.entering_name)
    dp.register_message_handler(enter_description, state=CreateTaskStates.entering_description)