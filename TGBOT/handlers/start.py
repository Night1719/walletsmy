from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from keyboards import phone_request_keyboard, main_menu_keyboard
from api_client import get_user_by_phone
from storage import get_session, set_session
from states import AuthStates


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    session = get_session(message.from_user.id)
    if session and session.get("intraservice_id"):
        await message.answer(
            f"Снова здравствуйте, {session.get('name', 'пользователь')}!", reply_markup=main_menu_keyboard()
        )
        return

    await AuthStates.awaiting_phone.set()
    await message.answer(
        "Добро пожаловать! Отправьте номер телефона для авторизации в Helpdesk.",
        reply_markup=phone_request_keyboard()
    )


async def handle_contact(message: types.Message, state: FSMContext):
    if not message.contact or not message.contact.phone_number:
        await message.answer("Не удалось получить телефон. Отправьте контакт или введите номер вручную.")
        return
    await _authorize(message, message.contact.phone_number)


async def handle_manual_phone(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()
    if text.startswith("✍️"):
        await message.answer("Введите номер телефона в формате +7XXXXXXXXXX или 8XXXXXXXXXX")
        return
    await _authorize(message, text)


async def _authorize(message: types.Message, phone: str):
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
        reply_markup=main_menu_keyboard()
    )
    await AuthStates.finish()


def register_start_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start", "help"], state="*")
    dp.register_message_handler(handle_contact, content_types=["contact"], state=AuthStates.awaiting_phone)
    dp.register_message_handler(handle_manual_phone, lambda m: m.text and not m.text.startswith("/"), content_types=["text"], state=AuthStates.awaiting_phone)