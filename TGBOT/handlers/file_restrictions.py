"""
Handler for blocking file uploads from users.
Prevents users from sending screenshots, images, and other files to the bot.
"""
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from config import BLOCK_FILE_UPLOADS, BLOCKED_UPLOAD_TYPES, ALLOWED_UPLOAD_CONTEXTS
from storage import get_session
import logging

router = Router()
logger = logging.getLogger(__name__)


def _is_upload_allowed_in_context(state: FSMContext) -> bool:
    """Check if file upload is allowed in current context"""
    if not ALLOWED_UPLOAD_CONTEXTS:
        return False
    
    current_state = state.get_state()
    if not current_state:
        return False
    
    # Check if current state is in allowed contexts
    for allowed_context in ALLOWED_UPLOAD_CONTEXTS:
        if allowed_context and allowed_context in current_state:
            return True
    
    return False


def _get_file_type_name(file_type: str) -> str:
    """Get human-readable name for file type"""
    type_names = {
        'photo': 'фотографии',
        'document': 'документы',
        'sticker': 'стикеры',
        'video': 'видео',
        'voice': 'голосовые сообщения',
        'video_note': 'видеосообщения',
        'animation': 'анимации (GIF)',
        'audio': 'аудиофайлы',
        'contact': 'контакты',
        'location': 'геолокацию',
        'venue': 'места',
        'poll': 'опросы',
        'dice': 'кости',
        'dart': 'дротики',
        'new_chat_members': 'новых участников',
        'left_chat_member': 'покинувших участников',
        'new_chat_title': 'новые названия чата',
        'new_chat_photo': 'новые фото чата',
        'delete_chat_photo': 'удаление фото чата',
        'group_chat_created': 'создание группового чата',
        'supergroup_chat_created': 'создание супергруппы',
        'channel_chat_created': 'создание канала',
        'migrate_to_chat_id': 'миграцию чата',
        'migrate_from_chat_id': 'миграцию из чата',
        'pinned_message': 'закрепленные сообщения',
        'invoice': 'счета',
        'successful_payment': 'успешные платежи',
        'connected_website': 'подключенные сайты',
        'passport_data': 'данные паспорта',
        'proximity_alert_triggered': 'срабатывание геозоны',
    }
    return type_names.get(file_type, file_type)


def _get_block_message(file_type: str) -> str:
    """Get appropriate block message for file type"""
    type_name = _get_file_type_name(file_type)
    
    if file_type in ['photo', 'document']:
        return (
            f"🚫 Загрузка {type_name} запрещена.\n\n"
            f"❌ Нельзя отправлять:\n"
            f"• Скриншоты и фотографии\n"
            f"• Документы и файлы\n"
            f"• Изображения\n\n"
            f"✅ Используйте текстовые сообщения для общения с ботом.\n"
            f"📚 Для получения инструкций используйте раздел 'Инструкции'."
        )
    elif file_type in ['sticker', 'animation']:
        return (
            f"🚫 Отправка {type_name} запрещена.\n\n"
            f"❌ Нельзя отправлять:\n"
            f"• Стикеры и анимации\n"
            f"• GIF-файлы\n\n"
            f"✅ Используйте текстовые сообщения для общения с ботом."
        )
    elif file_type in ['video', 'voice', 'video_note']:
        return (
            f"🚫 Отправка {type_name} запрещена.\n\n"
            f"❌ Нельзя отправлять:\n"
            f"• Видео и аудио\n"
            f"• Голосовые сообщения\n\n"
            f"✅ Используйте текстовые сообщения для общения с ботом."
        )
    else:
        return (
            f"🚫 Отправка {type_name} запрещена.\n\n"
            f"❌ Этот тип контента не поддерживается.\n\n"
            f"✅ Используйте текстовые сообщения для общения с ботом."
        )


@router.message(F.photo)
async def block_photo_upload(message: types.Message, state: FSMContext):
    """Block photo uploads (screenshots)"""
    if not BLOCK_FILE_UPLOADS:
        return
    
    if _is_upload_allowed_in_context(state):
        return
    
    logger.warning(f"User {message.from_user.id} attempted to upload photo")
    await message.answer(_get_block_message('photo'))


@router.message(F.document)
async def block_document_upload(message: types.Message, state: FSMContext):
    """Block document uploads"""
    if not BLOCK_FILE_UPLOADS:
        return
    
    if _is_upload_allowed_in_context(state):
        return
    
    # Check if it's an image disguised as document
    if message.document.mime_type and message.document.mime_type.startswith('image/'):
        logger.warning(f"User {message.from_user.id} attempted to upload image as document: {message.document.file_name}")
        await message.answer(
            "🚫 Загрузка изображений запрещена.\n\n"
            "❌ Нельзя отправлять:\n"
            "• Скриншоты и фотографии\n"
            "• Изображения в любом формате\n\n"
            "✅ Используйте текстовые сообщения для общения с ботом.\n"
            "📚 Для получения инструкций используйте раздел 'Инструкции'."
        )
        return
    
    # Check file extension for common image formats
    if message.document.file_name:
        file_ext = message.document.file_name.lower().split('.')[-1]
        image_extensions = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'ico', 'svg']
        if file_ext in image_extensions:
            logger.warning(f"User {message.from_user.id} attempted to upload image with document extension: {message.document.file_name}")
            await message.answer(
                "🚫 Загрузка изображений запрещена.\n\n"
                "❌ Нельзя отправлять:\n"
                "• Скриншоты и фотографии\n"
                "• Изображения в любом формате\n\n"
                "✅ Используйте текстовые сообщения для общения с ботом.\n"
                "📚 Для получения инструкций используйте раздел 'Инструкции'."
            )
            return
    
    # Check for screenshot-related keywords in filename
    if message.document.file_name:
        filename_lower = message.document.file_name.lower()
        screenshot_keywords = [
            'screenshot', 'скриншот', 'screen', 'экран', 'capture', 'захват',
            'print', 'печать', 'screen_', 'img_', 'photo', 'фото', 'picture', 'картинка'
        ]
        if any(keyword in filename_lower for keyword in screenshot_keywords):
            logger.warning(f"User {message.from_user.id} attempted to upload file with screenshot name: {message.document.file_name}")
            await message.answer(
                "🚫 Загрузка скриншотов запрещена.\n\n"
                "❌ Нельзя отправлять:\n"
                "• Скриншоты и фотографии\n"
                "• Файлы с названиями, содержащими 'скриншот', 'screenshot' и т.д.\n\n"
                "✅ Используйте текстовые сообщения для общения с ботом.\n"
                "📚 Для получения инструкций используйте раздел 'Инструкции'."
            )
            return
    
    logger.warning(f"User {message.from_user.id} attempted to upload document: {message.document.file_name}")
    await message.answer(_get_block_message('document'))


@router.message(F.sticker)
async def block_sticker_upload(message: types.Message, state: FSMContext):
    """Block sticker uploads"""
    if not BLOCK_FILE_UPLOADS:
        return
    
    if _is_upload_allowed_in_context(state):
        return
    
    logger.warning(f"User {message.from_user.id} attempted to send sticker")
    await message.answer(_get_block_message('sticker'))


@router.message(F.video)
async def block_video_upload(message: types.Message, state: FSMContext):
    """Block video uploads"""
    if not BLOCK_FILE_UPLOADS:
        return
    
    if _is_upload_allowed_in_context(state):
        return
    
    logger.warning(f"User {message.from_user.id} attempted to upload video")
    await message.answer(_get_block_message('video'))


@router.message(F.voice)
async def block_voice_upload(message: types.Message, state: FSMContext):
    """Block voice message uploads"""
    if not BLOCK_FILE_UPLOADS:
        return
    
    if _is_upload_allowed_in_context(state):
        return
    
    logger.warning(f"User {message.from_user.id} attempted to send voice message")
    await message.answer(_get_block_message('voice'))


@router.message(F.video_note)
async def block_video_note_upload(message: types.Message, state: FSMContext):
    """Block video note uploads"""
    if not BLOCK_FILE_UPLOADS:
        return
    
    if _is_upload_allowed_in_context(state):
        return
    
    logger.warning(f"User {message.from_user.id} attempted to send video note")
    await message.answer(_get_block_message('video_note'))


@router.message(F.animation)
async def block_animation_upload(message: types.Message, state: FSMContext):
    """Block animation (GIF) uploads"""
    if not BLOCK_FILE_UPLOADS:
        return
    
    if _is_upload_allowed_in_context(state):
        return
    
    logger.warning(f"User {message.from_user.id} attempted to send animation")
    await message.answer(_get_block_message('animation'))


@router.message(F.audio)
async def block_audio_upload(message: types.Message, state: FSMContext):
    """Block audio file uploads"""
    if not BLOCK_FILE_UPLOADS:
        return
    
    if _is_upload_allowed_in_context(state):
        return
    
    logger.warning(f"User {message.from_user.id} attempted to upload audio")
    await message.answer(_get_block_message('audio'))


@router.message(F.contact)
async def block_contact_upload(message: types.Message, state: FSMContext):
    """Block contact sharing"""
    if not BLOCK_FILE_UPLOADS:
        return
    
    if _is_upload_allowed_in_context(state):
        return
    
    logger.warning(f"User {message.from_user.id} attempted to share contact")
    await message.answer(
        "🚫 Отправка контактов запрещена.\n\n"
        "❌ Нельзя отправлять:\n"
        "• Контакты и визитки\n\n"
        "✅ Используйте текстовые сообщения для общения с ботом."
    )


@router.message(F.location)
async def block_location_upload(message: types.Message, state: FSMContext):
    """Block location sharing"""
    if not BLOCK_FILE_UPLOADS:
        return
    
    if _is_upload_allowed_in_context(state):
        return
    
    logger.warning(f"User {message.from_user.id} attempted to share location")
    await message.answer(
        "🚫 Отправка геолокации запрещена.\n\n"
        "❌ Нельзя отправлять:\n"
        "• Местоположение и геолокацию\n\n"
        "✅ Используйте текстовые сообщения для общения с ботом."
    )


@router.message(F.poll)
async def block_poll_upload(message: types.Message, state: FSMContext):
    """Block poll creation"""
    if not BLOCK_FILE_UPLOADS:
        return
    
    if _is_upload_allowed_in_context(state):
        return
    
    logger.warning(f"User {message.from_user.id} attempted to create poll")
    await message.answer(
        "🚫 Создание опросов запрещено.\n\n"
        "❌ Нельзя создавать:\n"
        "• Опросы и голосования\n\n"
        "✅ Используйте текстовые сообщения для общения с ботом."
    )


@router.message(F.dice)
async def block_dice_upload(message: types.Message, state: FSMContext):
    """Block dice sending"""
    if not BLOCK_FILE_UPLOADS:
        return
    
    if _is_upload_allowed_in_context(state):
        return
    
    logger.warning(f"User {message.from_user.id} attempted to send dice")
    await message.answer(
        "🚫 Отправка игр запрещена.\n\n"
        "❌ Нельзя отправлять:\n"
        "• Игры (кости, дротики и т.д.)\n\n"
        "✅ Используйте текстовые сообщения для общения с ботом."
    )


@router.message(F.venue)
async def block_venue_upload(message: types.Message, state: FSMContext):
    """Block venue sharing"""
    if not BLOCK_FILE_UPLOADS:
        return
    
    if _is_upload_allowed_in_context(state):
        return
    
    logger.warning(f"User {message.from_user.id} attempted to share venue")
    await message.answer(
        "🚫 Отправка мест запрещена.\n\n"
        "❌ Нельзя отправлять:\n"
        "• Места и заведения\n\n"
        "✅ Используйте текстовые сообщения для общения с ботом."
    )