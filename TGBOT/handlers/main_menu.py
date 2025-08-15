from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from keyboards import main_menu_keyboard, my_tasks_menu_keyboard
from storage import get_session


async def main_menu_entry(message: types.Message, state: FSMContext):
    session = get_session(message.from_user.id)
    if not session:
        await message.answer("Сначала авторизуйтесь командой /start")
        return
    await message.answer("Главное меню:", reply_markup=main_menu_keyboard())


async def open_my_tasks(message: types.Message, state: FSMContext):
    await message.answer("Выберите список:", reply_markup=my_tasks_menu_keyboard())


def register_main_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(main_menu_entry, commands=["menu"], state="*")
    dp.register_message_handler(open_my_tasks, lambda m: m.text and m.text.strip() == "📋 Мои заявки", state="*")