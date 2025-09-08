from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from keyboards import (
    instructions_main_keyboard, 
    instructions_1c_keyboard, 
    instructions_email_keyboard,
    instructions_otp_keyboard,
    main_menu_after_auth_keyboard
)
from aiogram.types import WebAppInfo
from storage import get_session
from states import InstructionsStates
from config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM, 
    SMTP_USE_TLS, SMTP_USE_SSL, CORP_EMAIL_DOMAIN, 
    INSTRUCTIONS_OTP_EXPIRE_MINUTES, MINIAPP_URL
)
from api_client import get_user_by_phone, get_user_by_email
from file_server import get_instruction_files, save_temp_file, cleanup_temp_file, get_instruction_info
import smtplib
from email.message import EmailMessage
import random
import time
import logging
import os

router = Router()
logger = logging.getLogger(__name__)

# Store OTP codes temporarily (in production, use Redis or database)
_otp_codes = {}


def _send_otp_email(email: str, otp: str) -> bool:
    """Send OTP code to email"""
    try:
        if not SMTP_HOST or not SMTP_FROM:
            logger.error("SMTP is not configured")
            return False
            
        msg = EmailMessage()
        msg['Subject'] = 'Код доступа к инструкциям'
        msg['From'] = SMTP_FROM
        msg['To'] = email
        msg.set_content(f"Ваш код доступа к инструкциям: {otp}. Действителен {INSTRUCTIONS_OTP_EXPIRE_MINUTES} минут.")
        
        if SMTP_USE_SSL:
            server_cls = smtplib.SMTP_SSL
        else:
            server_cls = smtplib.SMTP
            
        with server_cls(SMTP_HOST, SMTP_PORT) as s:
            if SMTP_USE_TLS and not SMTP_USE_SSL:
                s.starttls()
            if SMTP_USER:
                try:
                    s.login(SMTP_USER, SMTP_PASS)
                except smtplib.SMTPAuthenticationError:
                    # Try different user variants
                    user_variants = {SMTP_USER}
                    if "@" in SMTP_USER:
                        user_variants.add(SMTP_USER.split("@")[0])
                    else:
                        if "\\" in SMTP_USER:
                            user_variants.add(SMTP_USER.split("\\")[-1])
                    authed = False
                    for u in user_variants:
                        try:
                            s.login(u, SMTP_PASS)
                            authed = True
                            break
                        except smtplib.SMTPAuthenticationError:
                            continue
                    if not authed:
                        raise
            s.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP to {email}: {e}")
        return False


@router.message(F.text == "📚 Инструкции")
async def instructions_start(message: types.Message, state: FSMContext):
    """Start instructions access with OTP verification"""
    session = get_session(message.from_user.id)
    if not session:
        await message.answer("Сначала авторизуйтесь: /start")
        return
    
    # Check if user already has access to instructions
    if session.get("instructions_access"):
        await state.set_state(InstructionsStates.main_menu)
        await message.answer("📚 Раздел инструкций:", reply_markup=instructions_main_keyboard())
        return
    
    # Request phone for OTP verification
    await state.set_state(InstructionsStates.awaiting_otp_phone)
    await message.answer(
        "🔐 Для доступа к инструкциям требуется дополнительная авторизация.\n"
        "Отправьте ваш номер телефона:",
        reply_markup=instructions_otp_keyboard()
    )


@router.message(InstructionsStates.awaiting_otp_phone, F.contact)
async def instructions_phone_contact(message: types.Message, state: FSMContext):
    """Handle phone contact for instructions OTP"""
    if not message.contact or not message.contact.phone_number:
        await message.answer("Не удалось получить телефон. Попробуйте снова.")
        return
    
    phone = message.contact.phone_number
    user = get_user_by_phone(phone)
    
    if not user:
        await message.answer("Пользователь не найден. Обратитесь к администратору.")
        await state.clear()
        return
    
    email = user.get("Email") or user.get("EMail")
    if not email:
        await message.answer("У пользователя не указан email. Обратитесь к администратору.")
        await state.clear()
        return
    
    # Generate and send OTP
    otp = str(random.randint(100000, 999999))
    otp_timestamp = int(time.time())
    
    _otp_codes[str(message.from_user.id)] = {
        "otp": otp,
        "timestamp": otp_timestamp,
        "email": email
    }
    
    if _send_otp_email(email, otp):
        await state.set_state(InstructionsStates.awaiting_otp_code)
        await message.answer(f"Код отправлен на {email}. Введите 6-значный код:")
    else:
        await message.answer("Не удалось отправить код. Обратитесь к администратору.")
        await state.clear()


@router.message(InstructionsStates.awaiting_otp_phone, F.text == "✍️ Ввести вручную")
async def instructions_phone_manual(message: types.Message, state: FSMContext):
    """Handle manual phone input for instructions OTP"""
    await message.answer("Введите номер телефона:")


@router.message(InstructionsStates.awaiting_otp_phone, F.text.regexp(r"^[\+]?[0-9\s\-\(\)]{10,}$"))
async def instructions_phone_manual_input(message: types.Message, state: FSMContext):
    """Handle manual phone number input"""
    phone = message.text.strip()
    user = get_user_by_phone(phone)
    
    if not user:
        await message.answer("Пользователь не найден. Обратитесь к администратору.")
        await state.clear()
        return
    
    email = user.get("Email") or user.get("EMail")
    if not email:
        await message.answer("У пользователя не указан email. Обратитесь к администратору.")
        await state.clear()
        return
    
    # Generate and send OTP
    otp = str(random.randint(100000, 999999))
    otp_timestamp = int(time.time())
    
    _otp_codes[str(message.from_user.id)] = {
        "otp": otp,
        "timestamp": otp_timestamp,
        "email": email
    }
    
    if _send_otp_email(email, otp):
        await state.set_state(InstructionsStates.awaiting_otp_code)
        await message.answer(f"Код отправлен на {email}. Введите 6-значный код:")
    else:
        await message.answer("Не удалось отправить код. Обратитесь к администратору.")
        await state.clear()


@router.message(InstructionsStates.awaiting_otp_code, F.text.regexp(r"^\d{6}$"))
async def instructions_verify_otp(message: types.Message, state: FSMContext):
    """Verify OTP code for instructions access"""
    user_id = str(message.from_user.id)
    otp_data = _otp_codes.get(user_id)
    
    if not otp_data:
        await message.answer("Сессия истекла. Нажмите 📚 Инструкции снова.")
        await state.clear()
        return
    
    if int(time.time()) - otp_data["timestamp"] > INSTRUCTIONS_OTP_EXPIRE_MINUTES * 60:
        await message.answer("Код истёк. Попробуйте снова.")
        del _otp_codes[user_id]
        await state.clear()
        return
    
    if message.text.strip() != otp_data["otp"]:
        await message.answer("Неверный код. Повторите попытку.")
        return
    
    # Grant access to instructions
    session = get_session(message.from_user.id)
    if session:
        session["instructions_access"] = True
        from storage import set_session
        set_session(message.from_user.id, session)
    
    # Clean up OTP
    del _otp_codes[user_id]
    
    await state.set_state(InstructionsStates.main_menu)
    await message.answer("✅ Доступ к инструкциям предоставлен!", reply_markup=instructions_main_keyboard())


@router.message(InstructionsStates.main_menu, F.text == "1️⃣ 1С")
async def instructions_1c(message: types.Message, state: FSMContext):
    """Show 1C instructions menu"""
    await state.set_state(InstructionsStates.choosing_1c_type)
    await message.answer("Выберите тип инструкции 1С:", reply_markup=instructions_1c_keyboard())


@router.message(InstructionsStates.main_menu, F.text == "📧 Почта")
async def instructions_email(message: types.Message, state: FSMContext):
    """Show email instructions menu"""
    await state.set_state(InstructionsStates.choosing_email_type)
    await message.answer("Выберите тип инструкции по почте:", reply_markup=instructions_email_keyboard())


@router.message(InstructionsStates.choosing_1c_type, F.text.in_({"AR2", "DM"}))
async def instructions_1c_type(message: types.Message, state: FSMContext):
    """Handle 1C instruction type selection"""
    instruction_type = f"1c_{message.text.lower()}"
    await _send_instruction_files(message, instruction_type)


@router.message(InstructionsStates.choosing_email_type, F.text.in_({"📱 iPhone", "🤖 Android", "💻 Outlook"}))
async def instructions_email_type(message: types.Message, state: FSMContext):
    """Handle email instruction type selection"""
    text = message.text
    if text == "📱 iPhone":
        instruction_type = "email_iphone"
    elif text == "🤖 Android":
        instruction_type = "email_android"
    elif text == "💻 Outlook":
        instruction_type = "email_outlook"
    else:
        await message.answer("Неизвестный тип инструкции.")
        return
    
    await _send_instruction_files(message, instruction_type)


async def _send_instruction_files(message: types.Message, instruction_type: str):
    """Send instruction files via Mini App"""
    # Get instruction info
    info = get_instruction_info(instruction_type)
    if not info["available"]:
        await message.answer("❌ Инструкции временно недоступны. Попробуйте позже.")
        return
    
    # Get available formats
    files = get_instruction_files(instruction_type)
    available_formats = [fmt for fmt, content in files.items() if content is not None]
    
    if not available_formats:
        await message.answer("❌ Инструкции временно недоступны. Попробуйте позже.")
        return
    
    # Create Mini App button
    web_app_info = WebAppInfo(url=MINIAPP_URL)
    
    # Create keyboard with Mini App button
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    kb.button(text="📚 Открыть инструкции", web_app=web_app_info)
    
    # Format message based on instruction type
    type_names = {
        "1c_ar2": "1С AR2",
        "1c_dm": "1С DM", 
        "email_iphone": "iPhone",
        "email_android": "Android",
        "email_outlook": "Outlook"
    }
    
    type_name = type_names.get(instruction_type, instruction_type)
    formats_text = ", ".join([fmt.upper() for fmt in available_formats])
    
    message_text = (
        f"📚 Инструкции: {type_name}\n\n"
        f"📄 Доступные форматы: {formats_text}\n\n"
        f"✅ Нажмите кнопку ниже для просмотра инструкций в удобном интерфейсе"
    )
    
    await message.answer(message_text, reply_markup=kb.as_markup())


@router.message(InstructionsStates.choosing_1c_type, F.text == "⬅️ Назад")
@router.message(InstructionsStates.choosing_email_type, F.text == "⬅️ Назад")
async def instructions_back_to_main(message: types.Message, state: FSMContext):
    """Back to instructions main menu"""
    await state.set_state(InstructionsStates.main_menu)
    await message.answer("📚 Раздел инструкций:", reply_markup=instructions_main_keyboard())


@router.message(InstructionsStates.main_menu, F.text == "⬅️ Назад")
async def instructions_back_to_root(message: types.Message, state: FSMContext):
    """Back to main menu"""
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_after_auth_keyboard())


@router.message(InstructionsStates.awaiting_otp_phone, F.text == "⬅️ Назад")
@router.message(InstructionsStates.awaiting_otp_code, F.text == "⬅️ Назад")
async def instructions_cancel_otp(message: types.Message, state: FSMContext):
    """Cancel OTP verification"""
    user_id = str(message.from_user.id)
    if user_id in _otp_codes:
        del _otp_codes[user_id]
    
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_after_auth_keyboard())