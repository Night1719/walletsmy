from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards import phone_request_keyboard, main_menu_keyboard
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from api_client import get_user_by_phone
from storage import get_session, set_session
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

    await state.set_state(AuthStates.awaiting_phone)
    await message.answer(
        "Добро пожаловать! Отправьте номер телефона для авторизации в Helpdesk.",
        reply_markup=phone_request_keyboard()
    )


@router.message(AuthStates.awaiting_phone, F.contact)
async def handle_contact(message: types.Message, state: FSMContext):
    if not message.contact or not message.contact.phone_number:
        await message.answer("Не удалось получить телефон. Отправьте контакт или введите номер вручную.")
        return
    await _authorize(message, state, message.contact.phone_number)


@router.message(AuthStates.awaiting_phone, F.text)
async def handle_manual_phone(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()
    if text.startswith("✍️"):
        await message.answer("Введите номер телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX")
        return
    await _authorize(message, state, text)


async def _authorize(message: types.Message, state: FSMContext, phone: str):
    user = get_user_by_phone(phone)
    if not user:
        await message.answer("Пользователь с таким номером не найден. Проверьте номер и попробуйте снова.")
        return

    session = {
        "intraservice_id": user.get("Id"),
        "phone": phone,
        "name": user.get("Name"),
        "stage": "main_menu",
    }
    set_session(message.from_user.id, session)

    await message.answer(
        f"✅ Авторизация успешна!\nЗдравствуйте, {user.get('Name')}",
        reply_markup=_post_auth_menu()
    )
    await state.clear()


def _post_auth_menu():
    kb = ReplyKeyboardBuilder()
    kb.row(types.KeyboardButton(text="🛠 Helpdesk"))
    kb.row(types.KeyboardButton(text="👤 Справочник сотрудников"))
    return kb.as_markup(resize_keyboard=True)