from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from keyboards import settings_menu_keyboard
from storage import get_session, get_preferences, set_preferences


async def open_settings(message: types.Message, state: FSMContext):
    if message.text.strip() != "⚙️ Настройки":
        return
    session = get_session(message.from_user.id)
    if not session:
        await message.answer("Сначала авторизуйтесь: /start")
        return
    prefs = get_preferences(message.from_user.id)
    await message.answer("Уведомления:", reply_markup=settings_menu_keyboard(prefs))


async def toggle_setting(call: types.CallbackQuery, state: FSMContext):
    data = call.data
    if not data.startswith("toggle:"):
        return
    key = data.split(":", 1)[1]
    prefs = get_preferences(call.from_user.id)
    if key in prefs:
        prefs[key] = not prefs[key]
        set_preferences(call.from_user.id, prefs)
    await call.message.edit_reply_markup(settings_menu_keyboard(prefs))
    await call.answer("Сохранено")


def register_settings_handlers(dp: Dispatcher):
    dp.register_message_handler(open_settings, content_types=["text"], state="*")
    dp.register_callback_query_handler(toggle_setting, lambda c: c.data.startswith("toggle:"), state="*")