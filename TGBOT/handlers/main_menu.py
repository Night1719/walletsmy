from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards import main_menu_keyboard, main_menu_after_auth_keyboard
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from api_client import search_users_by_name
from storage import get_session
from storage import get_session
from aiogram.filters import StateFilter

router = Router()


@router.message(F.text == "/menu")
async def main_menu_entry(message: types.Message, state: FSMContext):
    session = get_session(message.from_user.id)
    if not session:
        await message.answer("Сначала авторизуйтесь командой /start")
        return
    await message.answer("Главное меню:", reply_markup=main_menu_keyboard())


@router.message(F.text == "📋 Мои заявки")
async def open_my_tasks(message: types.Message, state: FSMContext):
    # Сразу показываем открытые заявки по CreatorId
    await state.clear()
    from handlers.my_tasks import send_my_open_tasks
    await send_my_open_tasks(message, state)


@router.message(F.text == "⬅️ Назад")
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_keyboard())


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
        for k in ("MobilePhone", "WorkPhone", "InternalPhone", "Phone"):
            v = u.get(k)
            if v:
                phones.append(str(v))
        phone_str = ", ".join(phones) if phones else "—"
        lines.append(f"{name}\nДолжность: {title}\nEmail: {email}\nТелефон(ы): {phone_str}")
    await message.answer("\n\n".join(lines))