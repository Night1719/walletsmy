"""
Admin interface for managing instructions dynamically.
Allows adding, editing, and removing instructions without code changes.
"""
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards import admin_keyboard, admin_categories_keyboard, admin_instructions_keyboard, admin_file_format_keyboard
from instruction_manager import get_instruction_manager
from config import ADMIN_USER_IDS
import logging
import os
from pathlib import Path

router = Router()
logger = logging.getLogger(__name__)

# Admin states
class AdminStates(StatesGroup):
    waiting_for_category_name = State()
    waiting_for_category_icon = State()
    waiting_for_instruction_name = State()
    waiting_for_instruction_description = State()
    waiting_for_file_upload = State()
    waiting_for_file_format = State()

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
        await callback.answer("❌ У вас нет прав администратора")
        return
    
    manager = get_instruction_manager()
    categories = manager.get_all_categories()
    
    text = "📁 <b>Управление категориями</b>\n\n"
    if categories:
        for cat in categories:
            text += f"• {cat['icon']} {cat['name']} (<code>{cat['id']}</code>)\n"
    else:
        text += "Категории не найдены"
    
    await callback.message.edit_text(
        text,
        reply_markup=admin_categories_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_add_category")
async def admin_add_category(callback: types.CallbackQuery, state: FSMContext):
    """Start adding new category"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора")
        return
    
    await callback.message.edit_text(
        "📁 <b>Добавление категории</b>\n\n"
        "Введите ID категории (латинские буквы, цифры, подчеркивания):\n"
        "Например: <code>network</code>, <code>software</code>, <code>hardware</code>",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_for_category_name)
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
            "❌ Категория с таким ID уже существует\n"
            "Попробуйте другой ID:"
        )
        return
    
    # Store category ID and ask for name
    await state.update_data(category_id=category_id)
    await message.answer(
        "✅ ID категории принят\n\n"
        "Теперь введите название категории:"
    )
    await state.set_state(AdminStates.waiting_for_category_icon)

@router.message(AdminStates.waiting_for_category_icon)
async def admin_add_category_icon(message: types.Message, state: FSMContext):
    """Process category name and ask for icon"""
    category_name = message.text.strip()
    
    if not category_name:
        await message.answer("❌ Название не может быть пустым\nПопробуйте еще раз:")
        return
    
    # Store category name and ask for icon
    await state.update_data(category_name=category_name)
    await message.answer(
        "✅ Название категории принято\n\n"
        "Теперь введите иконку (эмодзи) для категории:\n"
        "Например: 📁, 🔧, 💻, 📱"
    )
    await state.set_state(AdminStates.waiting_for_category_icon)

@router.message(AdminStates.waiting_for_category_icon)
async def admin_add_category_final(message: types.Message, state: FSMContext):
    """Process category icon and create category"""
    icon = message.text.strip()
    
    if not icon:
        await message.answer("❌ Иконка не может быть пустой\nПопробуйте еще раз:")
        return
    
    # Get stored data
    data = await state.get_data()
    category_id = data.get('category_id')
    category_name = data.get('category_name')
    
    if not category_id or not category_name:
        await message.answer("❌ Ошибка: данные не найдены. Начните заново.")
        await state.clear()
        return
    
    # Create category
    manager = get_instruction_manager()
    success = manager.add_category(category_id, category_name, icon)
    
    if success:
        await message.answer(
            f"✅ <b>Категория создана!</b>\n\n"
            f"ID: <code>{category_id}</code>\n"
            f"Название: {icon} {category_name}",
            parse_mode="HTML"
        )
    else:
        await message.answer("❌ Ошибка при создании категории")
    
    await state.clear()

@router.callback_query(F.data.startswith("admin_category_"))
async def admin_category_actions(callback: types.CallbackQuery):
    """Handle category actions"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора")
        return
    
    action = callback.data.replace("admin_category_", "")
    
    if action == "back":
        await admin_categories(callback)
    else:
        # Handle other category actions
        await callback.answer("Функция в разработке")

@router.callback_query(F.data == "admin_instructions")
async def admin_instructions(callback: types.CallbackQuery):
    """Show instructions management"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора")
        return
    
    manager = get_instruction_manager()
    categories = manager.get_all_categories()
    
    text = "📋 <b>Управление инструкциями</b>\n\n"
    if categories:
        for cat in categories:
            instructions = manager.get_instructions_by_category(cat['id'])
            text += f"<b>{cat['icon']} {cat['name']}</b> ({len(instructions)} инструкций)\n"
            for inst in instructions:
                text += f"  • {inst['name']}\n"
            text += "\n"
    else:
        text += "Категории не найдены"
    
    # Создаем клавиатуру для выбора категории
    kb = InlineKeyboardBuilder()
    
    if categories:
        for cat in categories:
            kb.button(
                text=f"{cat['icon']} {cat['name']}",
                callback_data=f"admin_category_{cat['id']}"
            )
    else:
        kb.button(text="❌ Категории не найдены", callback_data="no_categories")
    
    kb.button(text="➕ Добавить категорию", callback_data="admin_add_category")
    kb.button(text="⬅️ Назад", callback_data="admin_back")
    kb.adjust(1)
    
    await callback.message.edit_text(
        text,
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("admin_add_instruction_"))
async def admin_add_instruction(callback: types.CallbackQuery, state: FSMContext):
    """Start adding new instruction"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора")
        return
    
    category_id = callback.data.replace("admin_add_instruction_", "")
    await state.update_data(category_id=category_id)
    
    await callback.message.edit_text(
        "📋 <b>Добавление инструкции</b>\n\n"
        "Введите название инструкции:",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_for_instruction_name)
    await callback.answer()

@router.message(AdminStates.waiting_for_instruction_name)
async def admin_add_instruction_name(message: types.Message, state: FSMContext):
    """Process instruction name"""
    instruction_name = message.text.strip()
    
    if not instruction_name:
        await message.answer("❌ Название не может быть пустым\nПопробуйте еще раз:")
        return
    
    await state.update_data(instruction_name=instruction_name)
    await message.answer(
        "✅ Название инструкции принято\n\n"
        "Теперь введите описание инструкции:"
    )
    await state.set_state(AdminStates.waiting_for_instruction_description)

@router.message(AdminStates.waiting_for_instruction_description)
async def admin_add_instruction_description(message: types.Message, state: FSMContext):
    """Process instruction description"""
    description = message.text.strip()
    
    if not description:
        await message.answer("❌ Описание не может быть пустым\nПопробуйте еще раз:")
        return
    
    await state.update_data(description=description)
    
    # Ask for file format
    await message.answer(
        "✅ Описание инструкции принято\n\n"
        "Выберите формат файла:",
        reply_markup=admin_file_format_keyboard()
    )
    await state.set_state(AdminStates.waiting_for_file_format)

@router.callback_query(F.data.startswith("admin_file_format_"))
async def admin_file_format_selected(callback: types.CallbackQuery, state: FSMContext):
    """Process file format selection"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора")
        return
    
    file_format = callback.data.replace("admin_file_format_", "")
    await state.update_data(file_format=file_format)
    
    await callback.message.edit_text(
        f"📎 <b>Загрузка файла</b>\n\n"
        f"Формат: <code>{file_format}</code>\n\n"
        f"Отправьте файл в формате {file_format.upper()}:",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_for_file_upload)
    await callback.answer()

@router.message(AdminStates.waiting_for_file_upload, F.document)
async def admin_file_uploaded(message: types.Message, state: FSMContext):
    """Process uploaded file"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    document = message.document
    file_name = document.file_name
    file_id = document.file_id
    
    # Get stored data
    data = await state.get_data()
    category_id = data.get('category_id')
    instruction_name = data.get('instruction_name')
    description = data.get('description')
    file_format = data.get('file_format')
    
    if not all([category_id, instruction_name, description, file_format]):
        await message.answer("❌ Ошибка: данные не найдены. Начните заново.")
        await state.clear()
        return
    
    # Validate file format
    if not file_name.lower().endswith(f'.{file_format.lower()}'):
        await message.answer(
            f"❌ Неверный формат файла. Ожидается {file_format.upper()}, получен {file_name.split('.')[-1].upper()}\n"
            f"Попробуйте еще раз:"
        )
        return
    
    # Download file
    try:
        file = await message.bot.get_file(file_id)
        file_path = f"instructions/{category_id}/{instruction_name}.{file_format}"
        
        # Create directory if not exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Download file
        await message.bot.download_file(file.file_path, file_path)
        
        # Add instruction to manager
        manager = get_instruction_manager()
        success = manager.add_instruction(
            category_id=category_id,
            instruction_id=instruction_name.lower().replace(' ', '_'),
            name=instruction_name,
            description=description,
            file_format=file_format,
            file_path=file_path
        )
        
        if success:
            await message.answer(
                f"✅ <b>Инструкция создана!</b>\n\n"
                f"Категория: {category_id}\n"
                f"Название: {instruction_name}\n"
                f"Формат: {file_format.upper()}\n"
                f"Файл: {file_name}",
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Ошибка при создании инструкции")
    
    except Exception as e:
        logger.error(f"Error processing file upload: {e}")
        await message.answer("❌ Ошибка при обработке файла")
    
    await state.clear()

@router.message(AdminStates.waiting_for_file_upload)
async def admin_file_upload_invalid(message: types.Message):
    """Handle invalid file upload"""
    await message.answer(
        "❌ Пожалуйста, отправьте файл в виде документа\n"
        "Попробуйте еще раз:"
    )

@router.callback_query(F.data.startswith("admin_instruction_"))
async def admin_instruction_actions(callback: types.CallbackQuery):
    """Handle instruction actions"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора")
        return
    
    action = callback.data.replace("admin_instruction_", "")
    
    if action == "back":
        await admin_instructions(callback)
    else:
        # Handle other instruction actions
        await callback.answer("Функция в разработке")


@router.callback_query(F.data == "admin_back")
async def admin_back(callback: types.CallbackQuery):
    """Return to admin main menu"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора")
        return
    
    await callback.message.edit_text(
        "🔧 <b>Админ панель</b>\n\nВыберите действие:",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "no_categories")
async def no_categories(callback: types.CallbackQuery):
    """Handle no categories case"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора")
        return
    
    await callback.answer("❌ Категории не найдены. Создайте первую категорию.")
