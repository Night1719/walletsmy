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
import requests
from storage import get_session
from states import InstructionsStates
from config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM, 
    SMTP_USE_TLS, SMTP_USE_SSL, CORP_EMAIL_DOMAIN, 
    INSTRUCTIONS_OTP_EXPIRE_MINUTES, MINIAPP_URL, MINIAPP_WEBHOOK_URL
)
from api_client import get_user_by_phone, get_user_by_email
from file_server import get_instruction_files, save_temp_file, cleanup_temp_file, get_instruction_info
from instruction_manager import get_instruction_manager
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
    
    # Request email for OTP verification
    await state.set_state(InstructionsStates.awaiting_otp_phone)
    await message.answer(
        "🔐 Для доступа к инструкциям требуется дополнительная авторизация.\n"
        "Введите ваш корпоративный email:",
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

@router.message(InstructionsStates.main_menu)
async def instructions_dynamic_categories(message: types.Message, state: FSMContext):
    """Show dynamic instruction categories"""
    try:
        manager = get_instruction_manager()
        categories = manager.get_categories()
        
        # Create dynamic keyboard
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        kb = InlineKeyboardBuilder()
        
        for cat_id, category in categories.items():
            instructions_count = len(category["instructions"])
            kb.button(
                text=f"{category['icon']} {category['name']} ({instructions_count})",
                callback_data=f"category_{cat_id}"
            )
        
        kb.adjust(1)
        
        await message.answer(
            "📚 <b>Выберите категорию инструкций:</b>",
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error showing dynamic categories: {e}")
        await message.answer("❌ Ошибка загрузки инструкций. Попробуйте позже.")


@router.callback_query(F.data.startswith("category_"))
async def instructions_dynamic_category(callback: types.CallbackQuery):
    """Handle dynamic category selection"""
    try:
        category_id = callback.data.replace("category_", "")
        manager = get_instruction_manager()
        category = manager.get_category(category_id)
        
        if not category:
            await callback.answer("❌ Категория не найдена", show_alert=True)
            return
        
        instructions = manager.get_instructions(category_id)
        
        # Create dynamic keyboard for instructions
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        kb = InlineKeyboardBuilder()
        
        for inst_id, instruction in instructions.items():
            available_files = manager.get_available_files(category_id, inst_id)
            files_text = f"({len([f for f in available_files if f['exists']])} файлов)"
            kb.button(
                text=f"📝 {instruction['name']} {files_text}",
                callback_data=f"instruction_{category_id}_{inst_id}"
            )
        
        kb.button(text="⬅️ Назад", callback_data="back_to_categories")
        kb.adjust(1)
        
        text = f"📚 <b>{category['icon']} {category['name']}</b>\n\n"
        text += f"📄 Описание: {category['description']}\n\n"
        text += f"📝 Инструкций: {len(instructions)}\n\n"
        text += "Выберите инструкцию:"
        
        await callback.message.edit_text(
            text,
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error handling dynamic category: {e}")
        await callback.answer("❌ Ошибка загрузки категории", show_alert=True)

@router.callback_query(F.data.startswith("instruction_"))
async def instructions_dynamic_instruction(callback: types.CallbackQuery):
    """Handle dynamic instruction selection"""
    try:
        parts = callback.data.replace("instruction_", "").split("_", 1)
        category_id = parts[0]
        instruction_id = parts[1]
        
        manager = get_instruction_manager()
        instruction = manager.get_instruction(category_id, instruction_id)
        
        if not instruction:
            await callback.answer("❌ Инструкция не найдена", show_alert=True)
            return
        
        available_files = manager.get_available_files(category_id, instruction_id)
        existing_files = [f for f in available_files if f['exists']]
        
        if not existing_files:
            await callback.answer("❌ Файлы инструкции недоступны", show_alert=True)
            return
        
        # Create keyboard for file formats
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        kb = InlineKeyboardBuilder()
        
        for file_info in existing_files:
            kb.button(
                text=f"📄 {file_info['format'].upper()}",
                callback_data=f"secure_link:{category_id}_{instruction_id}:{file_info['format']}"
            )
        
        kb.button(text="⬅️ Назад", callback_data=f"category_{category_id}")
        kb.adjust(1)
        
        text = f"📝 <b>{instruction['name']}</b>\n\n"
        text += f"📄 Описание: {instruction['description']}\n\n"
        text += f"📁 Доступные форматы: {', '.join([f['format'].upper() for f in existing_files])}\n\n"
        text += "🔒 Выберите формат для безопасного просмотра (ссылка действительна 40 минут):"
        
        await callback.message.edit_text(
            text,
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error handling dynamic instruction: {e}")
        await callback.answer("❌ Ошибка загрузки инструкции", show_alert=True)

@router.callback_query(F.data == "back_to_categories")
async def instructions_back_to_categories(callback: types.CallbackQuery):
    """Back to categories list"""
    try:
        manager = get_instruction_manager()
        categories = manager.get_categories()
        
        # Create dynamic keyboard
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        kb = InlineKeyboardBuilder()
        
        for cat_id, category in categories.items():
            instructions_count = len(category["instructions"])
            kb.button(
                text=f"{category['icon']} {category['name']} ({instructions_count})",
                callback_data=f"category_{cat_id}"
            )
        
        kb.adjust(1)
        
        await callback.message.edit_text(
            "📚 <b>Выберите категорию инструкций:</b>",
            reply_markup=kb.as_markup(),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error going back to categories: {e}")
        await callback.answer("❌ Ошибка загрузки категорий", show_alert=True)

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
    """Send instruction files via secure Mini App links"""
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
    
    # Create keyboard with format buttons
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    
    for fmt in available_formats:
        kb.button(
            text=f"📄 {fmt.upper()}", 
            callback_data=f"secure_link:{instruction_type}:{fmt}"
        )
    
    kb.adjust(1)  # One button per row
    
    message_text = (
        f"📚 Инструкции: {type_name}\n\n"
        f"📄 Доступные форматы: {formats_text}\n\n"
        f"🔒 Выберите формат для безопасного просмотра (ссылка действительна 40 минут)"
    )
    
    await message.answer(message_text, reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith("secure_link:"))
async def create_secure_link(callback: types.CallbackQuery):
    """Create secure link for instruction file"""
    try:
        # Parse callback data
        _, instruction_data, file_format = callback.data.split(":", 2)
        
        # Handle both old format (instruction_type) and new format (category_instruction)
        if "_" in instruction_data and not instruction_data.startswith("1c_") and not instruction_data.startswith("email_"):
            # New format: category_instruction
            parts = instruction_data.split("_", 1)
            category_id = parts[0]
            instruction_id = parts[1]
            instruction_type = f"{category_id}_{instruction_id}"
        else:
            # Old format: instruction_type
            instruction_type = instruction_data
        
        # Get user ID
        user_id = callback.from_user.id
        
        # Create secure link via API
        api_url = f"{MINIAPP_WEBHOOK_URL.rstrip('/')}/api/secure/create-link"
        
        response = requests.post(api_url, json={
            "instruction_type": instruction_type,
            "file_format": file_format,
            "user_id": user_id
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            secure_url = data["secure_url"]
            expires_in = data["expires_in_minutes"]
            
            # Create Mini App button
            web_app_info = WebAppInfo(url=secure_url)
            
            # Format message
            type_names = {
                "1c_ar2": "1С AR2",
                "1c_dm": "1С DM", 
                "email_iphone": "iPhone",
                "email_android": "Android",
                "email_outlook": "Outlook"
            }
            
            type_name = type_names.get(instruction_type, instruction_type)
            
            message_text = (
                f"🔒 Безопасная ссылка создана\n\n"
                f"📚 Инструкция: {type_name} ({file_format.upper()})\n"
                f"⏰ Действительна: {expires_in} минут\n\n"
                f"✅ Нажмите кнопку для просмотра"
            )
            
            # Create keyboard with Mini App button
            from aiogram.utils.keyboard import InlineKeyboardBuilder
            kb = InlineKeyboardBuilder()
            kb.button(text="📚 Открыть инструкцию", web_app=web_app_info)
            
            await callback.message.edit_text(
                message_text, 
                reply_markup=kb.as_markup()
            )
            
        else:
            error_data = response.json() if response.content else {"error": "Unknown error"}
            await callback.answer(f"❌ Ошибка создания ссылки: {error_data.get('error', 'Unknown error')}", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error creating secure link: {e}")
        await callback.answer("❌ Ошибка создания безопасной ссылки", show_alert=True)
    
    await callback.answer()

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