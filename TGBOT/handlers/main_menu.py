from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards import main_menu_keyboard, main_menu_after_auth_keyboard
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from api_client import search_users_by_name
from storage import get_session
from aiogram.filters import StateFilter
import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "/menu")
async def main_menu_entry(message: types.Message, state: FSMContext):
    session = get_session(message.from_user.id)
    if not session:
        await message.answer("Сначала авторизуйтесь командой /start")
        return
    await message.answer("Главное меню:", reply_markup=main_menu_after_auth_keyboard())


@router.message(F.text == "📋 Мои заявки")
async def open_my_tasks(message: types.Message, state: FSMContext):
    # Сразу показываем открытые заявки по CreatorId
    await state.clear()
    from handlers.my_tasks import send_my_open_tasks
    await send_my_open_tasks(message, state)


@router.message(F.text == "⬅️ Назад")
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_after_auth_keyboard())


@router.message(F.text == "🛠 Helpdesk")
async def go_helpdesk(message: types.Message, state: FSMContext):
    session = get_session(message.from_user.id)
    if not session:
        await message.answer("Сначала авторизуйтесь: /start")
        return
    await message.answer("Меню Helpdesk:", reply_markup=main_menu_keyboard())


@router.message(F.text == "👤 Справочник сотрудников")
async def employee_directory_prompt(message: types.Message, state: FSMContext):
    session = get_session(message.from_user.id)
    if not session:
        await message.answer("Сначала авторизуйтесь: /start")
        return
    await message.answer("Введите фамилию или имя сотрудника для поиска:\n(или нажмите 🏠 Главное меню)")


@router.message(F.text == "📚 Инструкции")
async def instructions_prompt(message: types.Message, state: FSMContext):
    session = get_session(message.from_user.id)
    if not session:
        await message.answer("Сначала авторизуйтесь: /start")
        return
    # Redirect to instructions handler
    from handlers.instructions import instructions_start
    await instructions_start(message, state)


@router.message(F.text == "🏠 Главное меню")
async def back_to_root_from_helpdesk(message: types.Message, state: FSMContext):
    session = get_session(message.from_user.id)
    if not session:
        await message.answer("Сначала авторизуйтесь: /start")
        return
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_after_auth_keyboard())


@router.message(
    StateFilter(None),
    F.text.regexp(r"^[A-Za-zА-Яа-яЁё\-\s]{2,}$")
    & ~(
        (F.text == "Удаленный доступ") |
        (F.text == "Прочее") |
        (F.text == "⬅️ Назад") |
        (F.text == "❌ Отменить")
    )
)
async def employee_directory_search(message: types.Message, state: FSMContext):
    query = message.text.strip()
    users = search_users_by_name(query)[:10]
    if not users:
        await message.answer("Ничего не найдено. Уточните запрос.")
        return
    lines = []
    for u in users:
        name = u.get("Name") or "—"
        title = u.get("Title") or u.get("Position") or "—"
        email = u.get("Email") or u.get("EMail") or "—"
        phones = []
        logger.debug(f"ℹ️ Пользователь {u.get('Name', 'Unknown')}: проверяем телефоны")
        
        # Сначала проверяем мобильный телефон
        mobile_phone = u.get("MobilePhone") or ""
        mobile_phone_str = str(mobile_phone).strip() if mobile_phone else ""
        logger.debug(f"ℹ️ MobilePhone: '{mobile_phone_str}'")
        
        # Проверяем все поля телефонов
        for k in ("WorkPhone", "InternalPhone", "Phone", "Extension", "PhoneNumber", "InternalNumber", "WorkNumber", "ExtNumber"):
            v = u.get(k)
            if v:
                phone_str = str(v).strip()
                logger.debug(f"ℹ️ Поле {k}: '{phone_str}'")
                
                # Если это поле Phone и есть мобильный, сравниваем их
                if k == "Phone" and mobile_phone_str:
                    # Показываем Phone только если он отличается от мобильного
                    if phone_str != mobile_phone_str and not phone_str.startswith(mobile_phone_str):
                        phones.append(phone_str)
                        logger.debug(f"ℹ️ Добавляем Phone (отличается от мобильного): '{phone_str}'")
                    else:
                        logger.debug(f"ℹ️ Пропускаем Phone (совпадает с мобильным): '{phone_str}'")
                else:
                    # Для остальных полей проверяем, что это не мобильный номер
                    if not (phone_str.startswith('7') or phone_str.startswith('+7') or phone_str.startswith('8')):
                        phones.append(phone_str)
                        logger.debug(f"ℹ️ Добавляем телефон: '{phone_str}'")
                    else:
                        logger.debug(f"ℹ️ Пропускаем мобильный: '{phone_str}'")
        
        phone_str = ", ".join(phones) if phones else "—"
        logger.debug(f"ℹ️ Итоговые телефоны: '{phone_str}'")
        
        # Формируем сообщение с дополнительной информацией о звонке
        lines.append(f"{name}\nДолжность: {title}\nEmail: {email}\nТелефон(ы): {phone_str}\n📱 Для звонка с мобильного используйте номер: +73433125000 и добавочный {phone_str}")
    await message.answer("\n\n".join(lines))