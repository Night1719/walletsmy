"""
Admin interface for managing instructions dynamically.
Allows adding, editing, and removing instructions without code changes.
"""
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from keyboards import admin_keyboard, admin_categories_keyboard, admin_instructions_keyboard
from instruction_manager import get_instruction_manager
from config import ADMIN_USER_IDS
import logging
import os
from pathlib import Path

router = Router()
logger = logging.getLogger(__name__)

# Admin states
class AdminStates:
    waiting_for_category_name = "waiting_for_category_name"
    waiting_for_category_icon = "waiting_for_category_icon"
    waiting_for_instruction_name = "waiting_for_instruction_name"
    waiting_for_instruction_description = "waiting_for_instruction_description"
    waiting_for_file_upload = "waiting_for_file_upload"
    waiting_for_file_format = "waiting_for_file_format"

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_USER_IDS

@router.message(F.text == "🔧 Админ панель")
async def admin_panel(message: types.Message):
    """Show admin panel"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    await message.answer(
        "🔧 <b>Админ панель</b>\n\n"
        "Выберите действие:",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "admin_categories")
async def admin_categories(callback: types.CallbackQuery):
    """Show categories management"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора", show_alert=True)
        return
    
    manager = get_instruction_manager()
    categories = manager.get_categories()
    
    text = "📁 <b>Управление категориями</b>\n\n"
    for cat_id, category in categories.items():
        instructions_count = len(category["instructions"])
        text += f"{category['icon']} <b>{category['name']}</b>\n"
        text += f"   📝 Инструкций: {instructions_count}\n"
        text += f"   📄 Описание: {category['description']}\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=admin_categories_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_add_category")
async def admin_add_category_start(callback: types.CallbackQuery, state: FSMContext):
    """Start adding new category"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_for_category_name)
    await callback.message.edit_text(
        "📁 <b>Добавление новой категории</b>\n\n"
        "Введите ID категории (латинскими буквами, без пробелов):\n"
        "Например: <code>network</code>, <code>software</code>, <code>hardware</code>",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_category_name)
async def admin_add_category_name(message: types.Message, state: FSMContext):
    """Process category ID"""
    category_id = message.text.strip().lower()
    
    # Validate category ID
    if not category_id.replace('_', '').isalnum():
        await message.answer(
            "❌ ID категории может содержать только латинские буквы, цифры и подчеркивания\n"
            "Попробуйте еще раз:"
        )
        return
    
    manager = get_instruction_manager()
    if manager.get_category(category_id):
        await message.answer(
            f"❌ Категория <code>{category_id}</code> уже существует\n"
            "Введите другой ID:",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(category_id=category_id)
    await state.set_state(AdminStates.waiting_for_category_icon)
    await message.answer(
        f"✅ ID категории: <code>{category_id}</code>\n\n"
        "Теперь введите название категории:\n"
        "Например: <b>Сеть</b>, <b>Программное обеспечение</b>",
        parse_mode="HTML"
    )

@router.message(AdminStates.waiting_for_category_icon)
async def admin_add_category_icon(message: types.Message, state: FSMContext):
    """Process category name and ask for icon"""
    category_name = message.text.strip()
    
    await state.update_data(category_name=category_name)
    await state.set_state(AdminStates.waiting_for_category_icon)
    await message.answer(
        f"✅ Название: <b>{category_name}</b>\n\n"
        "Теперь введите иконку для категории:\n"
        "Например: 🌐, 💻, 🔧, 📱, 📊\n\n"
        "Или отправьте эмодзи:",
        parse_mode="HTML"
    )

@router.message(AdminStates.waiting_for_category_icon)
async def admin_add_category_finish(message: types.Message, state: FSMContext):
    """Finish adding category"""
    icon = message.text.strip()
    
    data = await state.get_data()
    category_id = data["category_id"]
    category_name = data["category_name"]
    
    manager = get_instruction_manager()
    success = manager.add_category(
        category_id=category_id,
        name=category_name,
        icon=icon,
        description=f"Категория {category_name}"
    )
    
    if success:
        await message.answer(
            f"✅ <b>Категория добавлена!</b>\n\n"
            f"🆔 ID: <code>{category_id}</code>\n"
            f"📝 Название: <b>{category_name}</b>\n"
            f"🎨 Иконка: {icon}\n\n"
            f"Теперь вы можете добавить инструкции в эту категорию.",
            reply_markup=admin_keyboard(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ Ошибка при добавлении категории. Попробуйте еще раз.",
            reply_markup=admin_keyboard()
        )
    
    await state.clear()

@router.callback_query(F.data.startswith("admin_category_"))
async def admin_category_instructions(callback: types.CallbackQuery):
    """Show instructions in category"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора", show_alert=True)
        return
    
    category_id = callback.data.replace("admin_category_", "")
    manager = get_instruction_manager()
    category = manager.get_category(category_id)
    
    if not category:
        await callback.answer("❌ Категория не найдена", show_alert=True)
        return
    
    instructions = manager.get_instructions(category_id)
    
    text = f"📁 <b>{category['icon']} {category['name']}</b>\n\n"
    text += f"📄 Описание: {category['description']}\n\n"
    text += f"📝 Инструкций: {len(instructions)}\n\n"
    
    if instructions:
        text += "<b>Инструкции:</b>\n"
        for inst_id, instruction in instructions.items():
            files_count = len(instruction["files"])
            text += f"• <b>{instruction['name']}</b>\n"
            text += f"  📄 Файлов: {files_count}\n"
            text += f"  📝 {instruction['description']}\n\n"
    else:
        text += "📝 Инструкций пока нет"
    
    await callback.message.edit_text(
        text,
        reply_markup=admin_instructions_keyboard(category_id),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("admin_add_instruction_"))
async def admin_add_instruction_start(callback: types.CallbackQuery, state: FSMContext):
    """Start adding new instruction"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора", show_alert=True)
        return
    
    category_id = callback.data.replace("admin_add_instruction_", "")
    await state.update_data(category_id=category_id)
    await state.set_state(AdminStates.waiting_for_instruction_name)
    
    await callback.message.edit_text(
        f"📝 <b>Добавление новой инструкции</b>\n\n"
        f"Категория: <b>{category_id}</b>\n\n"
        "Введите ID инструкции (латинскими буквами, без пробелов):\n"
        "Например: <code>setup</code>, <code>troubleshooting</code>, <code>guide</code>",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_instruction_name)
async def admin_add_instruction_name(message: types.Message, state: FSMContext):
    """Process instruction ID"""
    instruction_id = message.text.strip().lower()
    
    # Validate instruction ID
    if not instruction_id.replace('_', '').isalnum():
        await message.answer(
            "❌ ID инструкции может содержать только латинские буквы, цифры и подчеркивания\n"
            "Попробуйте еще раз:"
        )
        return
    
    data = await state.get_data()
    category_id = data["category_id"]
    
    manager = get_instruction_manager()
    if manager.get_instruction(category_id, instruction_id):
        await message.answer(
            f"❌ Инструкция <code>{instruction_id}</code> уже существует в категории <code>{category_id}</code>\n"
            "Введите другой ID:",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(instruction_id=instruction_id)
    await state.set_state(AdminStates.waiting_for_instruction_description)
    await message.answer(
        f"✅ ID инструкции: <code>{instruction_id}</code>\n\n"
        "Теперь введите название инструкции:\n"
        "Например: <b>Настройка сети</b>, <b>Устранение неполадок</b>",
        parse_mode="HTML"
    )

@router.message(AdminStates.waiting_for_instruction_description)
async def admin_add_instruction_description(message: types.Message, state: FSMContext):
    """Process instruction name and ask for description"""
    instruction_name = message.text.strip()
    
    await state.update_data(instruction_name=instruction_name)
    await state.set_state(AdminStates.waiting_for_instruction_description)
    await message.answer(
        f"✅ Название: <b>{instruction_name}</b>\n\n"
        "Теперь введите описание инструкции (необязательно):\n"
        "Или отправьте <code>пропустить</code> для пропуска",
        parse_mode="HTML"
    )

@router.message(AdminStates.waiting_for_instruction_description)
async def admin_add_instruction_finish(message: types.Message, state: FSMContext):
    """Finish adding instruction"""
    description = message.text.strip()
    if description.lower() == "пропустить":
        description = ""
    
    data = await state.get_data()
    category_id = data["category_id"]
    instruction_id = data["instruction_id"]
    instruction_name = data["instruction_name"]
    
    manager = get_instruction_manager()
    success = manager.add_instruction(
        category_id=category_id,
        instruction_id=instruction_id,
        name=instruction_name,
        description=description
    )
    
    if success:
        await message.answer(
            f"✅ <b>Инструкция добавлена!</b>\n\n"
            f"📁 Категория: <code>{category_id}</code>\n"
            f"🆔 ID: <code>{instruction_id}</code>\n"
            f"📝 Название: <b>{instruction_name}</b>\n"
            f"📄 Описание: {description or 'Не указано'}\n\n"
            f"Теперь вы можете загрузить файлы для этой инструкции.",
            reply_markup=admin_keyboard(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ Ошибка при добавлении инструкции. Попробуйте еще раз.",
            reply_markup=admin_keyboard()
        )
    
    await state.clear()

@router.callback_query(F.data.startswith("admin_upload_file_"))
async def admin_upload_file_start(callback: types.CallbackQuery, state: FSMContext):
    """Start file upload process"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора", show_alert=True)
        return
    
    # Parse category and instruction from callback data
    parts = callback.data.replace("admin_upload_file_", "").split("_")
    category_id = parts[0]
    instruction_id = "_".join(parts[1:])
    
    await state.update_data(
        category_id=category_id,
        instruction_id=instruction_id
    )
    await state.set_state(AdminStates.waiting_for_file_format)
    
    await callback.message.edit_text(
        f"📤 <b>Загрузка файла</b>\n\n"
        f"Категория: <code>{category_id}</code>\n"
        f"Инструкция: <code>{instruction_id}</code>\n\n"
        "Выберите формат файла:",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="📄 PDF", callback_data=f"format_pdf_{category_id}_{instruction_id}")],
                [types.InlineKeyboardButton(text="📝 DOCX", callback_data=f"format_docx_{category_id}_{instruction_id}")],
                [types.InlineKeyboardButton(text="📄 DOC", callback_data=f"format_doc_{category_id}_{instruction_id}")],
                [types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_category_{category_id}")]
            ]
        ),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("format_"))
async def admin_upload_file_format(callback: types.CallbackQuery, state: FSMContext):
    """Process file format selection"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора", show_alert=True)
        return
    
    parts = callback.data.replace("format_", "").split("_")
    file_format = parts[0]
    category_id = parts[1]
    instruction_id = "_".join(parts[2:])
    
    await state.update_data(
        file_format=file_format,
        category_id=category_id,
        instruction_id=instruction_id
    )
    await state.set_state(AdminStates.waiting_for_file_upload)
    
    await callback.message.edit_text(
        f"📤 <b>Загрузка файла</b>\n\n"
        f"Категория: <code>{category_id}</code>\n"
        f"Инструкция: <code>{instruction_id}</code>\n"
        f"Формат: <b>{file_format.upper()}</b>\n\n"
        "Отправьте файл в чат:",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_file_upload, F.document)
async def admin_upload_file_process(message: types.Message, state: FSMContext):
    """Process uploaded file"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    data = await state.get_data()
    category_id = data["category_id"]
    instruction_id = data["instruction_id"]
    file_format = data["file_format"]
    
    # Get file info
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_size = message.document.file_size
    
    # Validate file format
    expected_extensions = {
        "pdf": [".pdf"],
        "docx": [".docx"],
        "doc": [".doc"]
    }
    
    file_ext = Path(file_name).suffix.lower()
    if file_ext not in expected_extensions.get(file_format, []):
        await message.answer(
            f"❌ Неверный формат файла. Ожидается {file_format.upper()}, получен {file_ext}\n"
            "Попробуйте еще раз:"
        )
        return
    
    # Validate file size (max 50MB)
    if file_size > 50 * 1024 * 1024:
        await message.answer(
            "❌ Файл слишком большой. Максимальный размер: 50MB\n"
            "Попробуйте еще раз:"
        )
        return
    
    try:
        # Download file
        bot = message.bot
        file = await bot.get_file(file_id)
        file_path = f"{category_id}/{instruction_id}/{instruction_id}.{file_format}"
        
        # Create directory
        manager = get_instruction_manager()
        file_dir = manager.instructions_dir / category_id / instruction_id
        file_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        full_path = file_dir / f"{instruction_id}.{file_format}"
        await bot.download_file(file.file_path, full_path)
        
        # Add file to instruction
        success = manager.add_file(
            category_id=category_id,
            instruction_id=instruction_id,
            file_format=file_format,
            file_path=file_path
        )
        
        if success:
            await message.answer(
                f"✅ <b>Файл загружен!</b>\n\n"
                f"📁 Категория: <code>{category_id}</code>\n"
                f"📝 Инструкция: <code>{instruction_id}</code>\n"
                f"📄 Формат: <b>{file_format.upper()}</b>\n"
                f"📏 Размер: {file_size / 1024 / 1024:.1f} MB\n"
                f"📁 Путь: <code>{file_path}</code>",
                reply_markup=admin_keyboard(),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ Ошибка при добавлении файла в конфигурацию. Файл сохранен, но не добавлен в базу.",
                reply_markup=admin_keyboard()
            )
    
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        await message.answer(
            f"❌ Ошибка при загрузке файла: {str(e)}",
            reply_markup=admin_keyboard()
        )
    
    await state.clear()

@router.message(AdminStates.waiting_for_file_upload)
async def admin_upload_file_invalid(message: types.Message):
    """Handle invalid file upload"""
    await message.answer(
        "❌ Пожалуйста, отправьте файл (документ), а не текст.\n"
        "Попробуйте еще раз:"
    )

@router.callback_query(F.data == "admin_back")
async def admin_back(callback: types.CallbackQuery):
    """Back to admin panel"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🔧 <b>Админ панель</b>\n\n"
        "Выберите действие:",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()