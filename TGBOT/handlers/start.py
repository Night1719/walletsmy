from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards import phone_request_keyboard, main_menu_keyboard
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from storage import get_session, set_session
from api_client import get_user_by_phone, get_user_by_email, update_user
from states import AuthStates, RegistrationStates
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM, SMTP_USE_TLS, CORP_EMAIL_DOMAIN, OTP_EXPIRE_MINUTES
import smtplib
from email.message import EmailMessage
import random
import time

router = Router()


def _auth_or_reg_menu():
    kb = ReplyKeyboardBuilder()
    kb.row(types.KeyboardButton(text="🔐 Авторизоваться"))
    kb.row(types.KeyboardButton(text="📝 Регистрация"))
    return kb.as_markup(resize_keyboard=True)

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
    await message.answer("Добро пожаловать! Выберите действие.", reply_markup=_auth_or_reg_menu())
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
    # Если не нашли — начинаем регистрацию, сохраняем телефон и просим email
    await state.update_data(reg_phone=phone)
    await state.set_state(RegistrationStates.awaiting_email)
    await message.answer("Пользователь не найден. Введите ваш корпоративный email:")


@router.message(F.text == "📝 Регистрация")
async def reg_start(message: types.Message, state: FSMContext):
    await state.set_state(RegistrationStates.awaiting_phone)
    kb = ReplyKeyboardBuilder()
    kb.row(types.KeyboardButton(text="📱 Отправить телефон", request_contact=True))
    await message.answer("Отправьте ваш номер телефона кнопкой ниже.", reply_markup=kb.as_markup(resize_keyboard=True))


@router.message(RegistrationStates.awaiting_phone, F.contact)
async def reg_collect_phone(message: types.Message, state: FSMContext):
    if not message.contact or not message.contact.phone_number:
        await message.answer("Не удалось получить телефон. Попробуйте снова.")
        return
    await state.update_data(reg_phone=message.contact.phone_number)
    await state.set_state(RegistrationStates.awaiting_email)
    await message.answer("Введите ваш корпоративный email:")


@router.message(RegistrationStates.awaiting_email, F.text)
async def reg_collect_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    data = await state.get_data()
    phone = data.get("reg_phone")
    if not phone:
        await message.answer("Сначала отправьте номер телефона.")
        return
    # Валидируем домен
    if CORP_EMAIL_DOMAIN:
        domains = [d.strip().lower() for d in CORP_EMAIL_DOMAIN.replace(';', ',').split(',') if d.strip()]
        if domains and not any(email.lower().endswith('@' + d) for d in domains):
            await message.answer("Укажите корпоративный email (недопустимый домен).")
            return
    # Ищем пользователя по email
    user = get_user_by_email(email)
    if not user:
        await message.answer("Пользователь с таким email не найден. Проверьте адрес.")
        return
    await state.update_data(reg_email=email, reg_user_id=user.get('Id'))
    # Отправляем 6-значный код
    otp = str(random.randint(100000, 999999))
    await state.update_data(reg_otp=otp, reg_otp_ts=int(time.time()))
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Код подтверждения'
        msg['From'] = SMTP_FROM
        msg['To'] = email
        msg.set_content(f"Ваш код подтверждения: {otp}. Действителен {OTP_EXPIRE_MINUTES} минут.")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            if SMTP_USE_TLS:
                s.starttls()
            if SMTP_USER:
                s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        await state.set_state(RegistrationStates.confirming)
        await message.answer("Код отправлен на почту. Введите 6-значный код:")
    except Exception:
        await message.answer("Не удалось отправить код. Обратитесь к администратору.")


@router.message(RegistrationStates.confirming, F.text.regexp(r"^\d{6}$"))
async def reg_verify_otp(message: types.Message, state: FSMContext):
    data = await state.get_data()
    otp = data.get('reg_otp')
    ts = int(data.get('reg_otp_ts', 0))
    phone = data.get('reg_phone')
    user_id = data.get('reg_user_id')
    if not (otp and ts and phone and user_id):
        await message.answer("Сессия истекла. Нажмите /start.")
        await state.clear()
        return
    if int(time.time()) - ts > OTP_EXPIRE_MINUTES * 60:
        await message.answer("Код истёк. Нажмите /start и попробуйте снова.")
        await state.clear()
        return
    if message.text.strip() != otp:
        await message.answer("Неверный код. Повторите попытку.")
        return
    # Привязываем номер
    ok = update_user(int(user_id), MobilePhone=phone)
    if ok:
        await message.answer("Телефон успешно привязан. Теперь нажмите ‘🔐 Авторизоваться’.", reply_markup=_auth_or_reg_menu())
    else:
        await message.answer("Не удалось привязать телефон. Обратитесь к администратору.", reply_markup=_auth_or_reg_menu())
    await state.clear()


def _post_auth_menu():
    kb = ReplyKeyboardBuilder()
    kb.row(types.KeyboardButton(text="🛠 Helpdesk"))
    kb.row(types.KeyboardButton(text="👤 Справочник сотрудников"))
    return kb.as_markup(resize_keyboard=True)