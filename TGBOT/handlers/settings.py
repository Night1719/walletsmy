from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards import settings_menu_keyboard
from storage import get_session, get_preferences, set_preferences
from background import run_user_checks

router = Router()


@router.message(F.text == "⚙️ Настройки")
async def open_settings(message: types.Message, state: FSMContext):
    session = get_session(message.from_user.id)
    if not session:
        await message.answer("Сначала авторизуйтесь: /start")
        return
    prefs = get_preferences(message.from_user.id)
    # Подсказка для ручной проверки
    await message.answer("Уведомления:\n(для проверки нажмите: /test_notify)", reply_markup=settings_menu_keyboard(prefs))


@router.message(F.text == "/test_notify")
async def test_notify(message: types.Message, state: FSMContext):
    await run_user_checks(message.bot, message.from_user.id)
    await message.answer("Проверка уведомлений выполнена.")


@router.callback_query(F.data.startswith("toggle:"))
async def toggle_setting(call: types.CallbackQuery, state: FSMContext):
    key = call.data.split(":", 1)[1]
    prefs = get_preferences(call.from_user.id)
    if key in prefs:
        prefs[key] = not prefs[key]
        set_preferences(call.from_user.id, prefs)
    try:
        await call.message.edit_reply_markup(settings_menu_keyboard(prefs))
    except Exception:
        pass
    await call.answer("Сохранено")


@router.callback_query(F.data == "settings:back")
async def settings_back(call: types.CallbackQuery):
    await call.message.delete()
    await call.answer()