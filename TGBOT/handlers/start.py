from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards import phone_request_keyboard, main_menu_keyboard
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from storage import get_session, set_session
from api_client import get_user_by_phone
from states import AuthStates
from api_client import create_task
from config import REGISTRATION_SERVICE_ID, REGISTRATION_CREATOR_ID, REGISTRATION_STATUS_ID

router = Router()


@router.message(F.text.in_({"/start", "/help"}))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    session = get_session(message.from_user.id)
    if session and session.get("intraservice_id"):
        await message.answer(
            f"Снова здравствуйте, {session.get('name', 'пользователь')}!", reply_markup=main_menu_keyboard()
        )
        return

    # Меню авторизации
    kb = ReplyKeyboardBuilder()
    kb.row(types.KeyboardButton(text="🔐 Авторизоваться"))
    kb.row(types.KeyboardButton(text="📝 Регистрация"))
    await message.answer("Добро пожаловать! Выберите действие.", reply_markup=kb.as_markup(resize_keyboard=True))
@router.message(F.text == "🔐 Авторизоваться")
async def auth_start(message: types.Message, state: FSMContext):
    kb = ReplyKeyboardBuilder()
    kb.row(types.KeyboardButton(text="📱 Отправить телефон", request_contact=True))
    await state.set_state(AuthStates.awaiting_phone)
    await message.answer("Отправьте ваш номер телефона кнопкой ниже для авторизации.", reply_markup=kb.as_markup(resize_keyboard=True))


@router.message(AuthStates.awaiting_phone, F.contact)
async def auth_or_reg_by_phone(message: types.Message, state: FSMContext):
    if not message.contact or not message.contact.phone_number:
        await message.answer("Не удалось получить телефон. Попробуйте снова.")
        return
    phone = message.contact.phone_number
    user = get_user_by_phone(phone)
    if user:
        # Сохраняем сессию и открываем Helpdesk/Справочник
        session = {
            "intraservice_id": user.get("Id"),
            "phone": phone,
            "name": user.get("Name"),
            "stage": "main_menu",
        }
        set_session(message.from_user.id, session)
        await message.answer(f"✅ Авторизация успешна!\nЗдравствуйте, {user.get('Name')}", reply_markup=_post_auth_menu())
        await state.clear()
        return
    # Если не нашли — начинаем регистрацию, сохраняем телефон и просим ФИО
    await state.update_data(reg_phone=phone)
    await message.answer("Пользователь не найден. Введите ваше ФИО для регистрации:")


@router.message(F.text == "📝 Регистрация")
async def reg_start(message: types.Message, state: FSMContext):
    await state.set_state(AuthStates.awaiting_phone)
    kb = ReplyKeyboardBuilder()
    kb.row(types.KeyboardButton(text="📱 Отправить телефон", request_contact=True))
    await message.answer("Отправьте ваш номер телефона кнопкой ниже.", reply_markup=kb.as_markup(resize_keyboard=True))


@router.message(AuthStates.awaiting_phone, F.contact)
async def reg_collect_phone(message: types.Message, state: FSMContext):
    if not message.contact or not message.contact.phone_number:
        await message.answer("Не удалось получить телефон. Попробуйте снова.")
        return
    await state.update_data(reg_phone=message.contact.phone_number)
    await message.answer("Введите ваше ФИО полностью:")


@router.message(AuthStates.awaiting_phone, F.text)
async def reg_collect_name(message: types.Message, state: FSMContext):
    fio = message.text.strip()
    data = await state.get_data()
    phone = data.get("reg_phone")
    if not phone:
        await message.answer("Сначала отправьте номер телефона.")
        return

    # Создаём заявку в Helpdesk
    name = "Добавить номер телефона"
    description = f"Телефон: {phone}\nФИО: {fio}"
    payload = {
        "Name": name,
        "Description": description,
        "CreatorId": int(REGISTRATION_CREATOR_ID) if REGISTRATION_CREATOR_ID else None,
        "ServiceId": int(REGISTRATION_SERVICE_ID) if REGISTRATION_SERVICE_ID else None,
        "StatusId": REGISTRATION_STATUS_ID or 27,
    }
    task_id = create_task(**payload)

    if task_id:
        await message.answer(f"Запрос на регистрацию отправлен, ожидайте.\nЗаявка #{task_id}", reply_markup=_post_auth_menu())
    else:
        await message.answer("Запрос на регистрацию отправлен, ожидайте.", reply_markup=_post_auth_menu())
    await state.clear()


def _post_auth_menu():
    kb = ReplyKeyboardBuilder()
    kb.row(types.KeyboardButton(text="🛠 Helpdesk"))
    kb.row(types.KeyboardButton(text="👤 Справочник сотрудников"))
    return kb.as_markup(resize_keyboard=True)