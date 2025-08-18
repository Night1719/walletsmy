from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards import phone_request_keyboard, main_menu_keyboard
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from storage import get_session
from states import AuthStates

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

    # Меню регистрации
    kb = ReplyKeyboardBuilder()
    kb.row(types.KeyboardButton(text="📝 Регистрация", request_contact=False))
    await message.answer("Добро пожаловать! Для продолжения нажмите ‘📝 Регистрация’.", reply_markup=kb.as_markup(resize_keyboard=True))


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
    # TODO: сохранить заявку на регистрацию (в БД/файл/отправка)
    await message.answer("Запрос на регистрацию отправлен, ожидайте.", reply_markup=_post_auth_menu())
    await state.clear()


def _post_auth_menu():
    kb = ReplyKeyboardBuilder()
    kb.row(types.KeyboardButton(text="🛠 Helpdesk"))
    kb.row(types.KeyboardButton(text="👤 Справочник сотрудников"))
    return kb.as_markup(resize_keyboard=True)