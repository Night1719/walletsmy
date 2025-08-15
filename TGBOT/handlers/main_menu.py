from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards import main_menu_keyboard, my_tasks_menu_keyboard
from storage import get_session

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
    await message.answer("Выберите список:", reply_markup=my_tasks_menu_keyboard())