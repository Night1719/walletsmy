"""
Instructions handlers with email OTP verification.
Fixed version for Windows users.
"""
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards import instructions_main_keyboard, instructions_category_keyboard, instruction_keyboard, otp_verification_keyboard, main_menu_after_auth_keyboard
from states import InstructionsStates
from storage import get_session, set_session
from file_server import get_instruction_files, get_instruction_info
from config import MINIAPP_URL, MINIAPP_MODE, CORP_EMAIL_DOMAIN, INSTRUCTIONS_OTP_EXPIRE_MINUTES
from instruction_manager import get_instruction_manager
import random
import time
import logging
import smtplib
from email.message import EmailMessage
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM, SMTP_USE_TLS, SMTP_USE_SSL

router = Router()
logger = logging.getLogger(__name__)

# Store OTP codes temporarily
_otp_codes = {}

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
    
    # Request email for OTP verification
    await state.set_state(InstructionsStates.awaiting_otp_phone)
    await message.answer(
        "🔐 Для доступа к инструкциям требуется дополнительная авторизация.\n"
        "Введите ваш корпоративный email:",
        reply_markup=otp_verification_keyboard()
    )


@router.message(InstructionsStates.awaiting_otp_phone, F.text)
async def instructions_email_input(message: types.Message, state: FSMContext):
    """Handle email input for instructions OTP"""
    email = message.text.strip()
    
    # Validate email format
    if "@" not in email or "." not in email.split("@")[1]:
        await message.answer("❌ Неверный формат email. Попробуйте еще раз:")
        return
    
    # Validate corporate domain if configured
    if CORP_EMAIL_DOMAIN:
        domains = [d.strip().lower() for d in CORP_EMAIL_DOMAIN.replace(';', ',').split(',') if d.strip()]
        if domains and not any(email.lower().endswith('@' + d) for d in domains):
            await message.answer("❌ Укажите корпоративный email (недопустимый домен).")
            return
    
    # Generate and send OTP
    otp = str(random.randint(100000, 999999))
    otp_timestamp = int(time.time())
    
    _otp_codes[str(message.from_user.id)] = {
        "code": otp,
        "timestamp": otp_timestamp,
        "email": email
    }
    
    # Send OTP via email
    try:
        if not SMTP_HOST or not SMTP_FROM:
            raise RuntimeError("SMTP not configured")
        
        msg = EmailMessage()
        msg['Subject'] = 'Код доступа к инструкциям'
        msg['From'] = SMTP_FROM
        msg['To'] = email
        msg.set_content(f'Ваш код доступа к инструкциям: {otp}\n\nКод действителен 5 минут.')
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            if SMTP_USE_TLS:
                s.starttls()
            if SMTP_USER and SMTP_PASS:
                s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        
        await message.answer(
            f"📧 Код отправлен на email {email}\n"
            "Введите код для подтверждения:"
        )
        await state.set_state(InstructionsStates.awaiting_otp_code)
        
    except Exception as e:
        logger.error(f"Error sending OTP email: {e}")
        await message.answer(
            f"❌ Ошибка отправки email. Код: {otp}\n"
            "Введите код для подтверждения:"
        )
        await state.set_state(InstructionsStates.awaiting_otp_code)


@router.message(InstructionsStates.awaiting_otp_code, F.text)
async def instructions_otp_verify(message: types.Message, state: FSMContext):
    """Verify OTP code for instructions access"""
    user_id = str(message.from_user.id)
    entered_code = message.text.strip()
    
    if user_id not in _otp_codes:
        await message.answer("❌ Код не найден. Начните заново.")
        await state.clear()
        return
    
    otp_data = _otp_codes[user_id]
    current_time = int(time.time())
    
    # Check if code expired
    if current_time - otp_data["timestamp"] > INSTRUCTIONS_OTP_EXPIRE_MINUTES * 60:
        await message.answer("❌ Код истек. Начните заново.")
        del _otp_codes[user_id]
        await state.clear()
        return
    
    # Verify code
    if entered_code != otp_data["code"]:
        await message.answer("❌ Неверный код. Попробуйте еще раз:")
        return
    
    # Success - grant access
    del _otp_codes[user_id]
    
    # Update session
    session = get_session(message.from_user.id)
    session["instructions_access"] = True
    set_session(message.from_user.id, session)
    
    await state.set_state(InstructionsStates.main_menu)
    await message.answer(
        "✅ Доступ к инструкциям предоставлен!\n\n"
        "📚 Выберите категорию:",
        reply_markup=instructions_main_keyboard()
    )


@router.callback_query(F.data == "resend_otp")
async def resend_otp(callback: types.CallbackQuery, state: FSMContext):
    """Resend OTP code"""
    user_id = str(callback.from_user.id)
    
    if user_id not in _otp_codes:
        await callback.answer("❌ Код не найден. Начните заново.")
        return
    
    otp_data = _otp_codes[user_id]
    email = otp_data["email"]
    
    # Generate new OTP
    otp = str(random.randint(100000, 999999))
    otp_timestamp = int(time.time())
    
    _otp_codes[user_id] = {
        "code": otp,
        "timestamp": otp_timestamp,
        "email": email
    }
    
    # Send new OTP
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Код доступа к инструкциям (повторно)'
        msg['From'] = SMTP_FROM
        msg['To'] = email
        msg.set_content(f'Ваш новый код доступа к инструкциям: {otp}\n\nКод действителен 5 минут.')
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            if SMTP_USE_TLS:
                s.starttls()
            if SMTP_USER and SMTP_PASS:
                s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        
        await callback.answer("📧 Новый код отправлен на email")
        
    except Exception as e:
        logger.error(f"Error resending OTP: {e}")
        await callback.answer("❌ Ошибка отправки. Попробуйте позже.")


@router.callback_query(F.data == "cancel_otp")
async def cancel_otp(callback: types.CallbackQuery, state: FSMContext):
    """Cancel OTP verification"""
    user_id = str(callback.from_user.id)
    if user_id in _otp_codes:
        del _otp_codes[user_id]
    
    await state.clear()
    await callback.message.edit_text("❌ Авторизация отменена")
    await callback.answer()


@router.callback_query(F.data == "close_instructions")
async def close_instructions(callback: types.CallbackQuery, state: FSMContext):
    """Close instructions menu"""
    await state.clear()
    await callback.message.edit_text("📚 Инструкции закрыты")
    await callback.answer()


@router.callback_query(F.data.startswith("category_"))
async def category_selected(callback: types.CallbackQuery, state: FSMContext):
    """Handle category selection"""
    category_id = callback.data.replace("category_", "")
    
    manager = get_instruction_manager()
    category = manager.get_category(category_id)
    
    if not category:
        await callback.answer("❌ Категория не найдена")
        return
    
    instructions = manager.get_instructions_by_category(category_id)
    
    if not instructions:
        await callback.message.edit_text(
            f"📁 {category['icon']} {category['name']}\n\n"
            "❌ Инструкции не найдены",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories")
            ]])
        )
    else:
        await callback.message.edit_text(
            f"📁 {category['icon']} {category['name']}\n\n"
            "Выберите инструкцию:",
            reply_markup=instructions_category_keyboard(category_id)
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("instruction_"))
async def instruction_selected(callback: types.CallbackQuery, state: FSMContext):
    """Handle instruction selection"""
    parts = callback.data.replace("instruction_", "").split("_")
    if len(parts) != 2:
        await callback.answer("❌ Ошибка данных")
        return
    
    category_id, instruction_id = parts
    
    manager = get_instruction_manager()
    instruction = manager.get_instruction(category_id, instruction_id)
    
    if not instruction:
        await callback.answer("❌ Инструкция не найдена")
        return
    
    await callback.message.edit_text(
        f"📄 {instruction['name']}\n\n"
        f"📝 {instruction['description']}\n\n"
        "Выберите формат файла:",
        reply_markup=instruction_keyboard(category_id, instruction_id)
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: types.CallbackQuery, state: FSMContext):
    """Return to categories list"""
    await callback.message.edit_text(
        "📚 Выберите категорию:",
        reply_markup=instructions_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("create_secure_link_"))
async def create_secure_link(callback: types.CallbackQuery, state: FSMContext):
    """Create secure link for instruction file"""
    parts = callback.data.replace("create_secure_link_", "").split("_")
    if len(parts) != 3:
        await callback.answer("❌ Ошибка данных")
        return
    
    category_id, instruction_id, file_format = parts
    
    manager = get_instruction_manager()
    instruction = manager.get_instruction(category_id, instruction_id)
    
    if not instruction:
        await callback.answer("❌ Инструкция не найдена")
        return
    
    # Create secure link via Mini App API
    try:
        import requests
        
        # Prepare data for Mini App API
        instruction_data = f"{category_id}_{instruction_id}"
        
        # Call Mini App API to create secure link
        miniapp_api_url = f"{MINIAPP_URL.replace('/miniapp', '')}/api/secure/create-link"
        
        response = requests.post(miniapp_api_url, json={
            "instruction_data": instruction_data,
            "file_format": file_format,
            "user_id": callback.from_user.id
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            secure_url = data.get("secure_url")
            
            if secure_url:
                # Send Mini App button
                await callback.message.edit_text(
                    f"📄 {instruction['name']} ({file_format.upper()})\n\n"
                    f"🔗 Ссылка действительна 40 минут\n\n"
                    "Нажмите кнопку ниже для просмотра:",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                        InlineKeyboardButton(
                            text="📱 Открыть инструкцию",
                            web_app=types.WebAppInfo(url=secure_url)
                        )
                    ], [
                        InlineKeyboardButton(text="⬅️ Назад", callback_data=f"instruction_{category_id}_{instruction_id}")
                    ]])
                )
            else:
                await callback.answer("❌ Ошибка создания ссылки")
        else:
            await callback.answer("❌ Ошибка сервера")
    
    except Exception as e:
        logger.error(f"Error creating secure link: {e}")
        await callback.answer("❌ Ошибка подключения к серверу")


@router.message(InstructionsStates.main_menu)
async def instructions_main_menu_handler(message: types.Message, state: FSMContext):
    """Handle main menu navigation"""
    if message.text == "🏠 Главное меню":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=main_menu_after_auth_keyboard())
    else:
        # Show inline categories again
        await message.answer(
            "📚 Выберите категорию:",
            reply_markup=instructions_main_keyboard()
        )