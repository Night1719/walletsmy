# 🔧 Исправление кнопки "Инструкции" в главном меню

## ❌ Проблема:
В главном меню отсутствует кнопка "📚 Инструкции" для доступа к Mini App.

## ✅ Решение:

### **Шаг 1: Проверьте файл `keyboards.py`**

Убедитесь, что функция `main_menu_after_auth_keyboard()` содержит кнопку "📚 Инструкции":

```python
def main_menu_after_auth_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🛠 Helpdesk"))
    kb.row(KeyboardButton(text="👤 Справочник сотрудников"))
    kb.row(KeyboardButton(text="📚 Инструкции"))  # ← Эта кнопка должна быть
    kb.row(KeyboardButton(text="🔧 Админ панель"))
    return kb.as_markup(resize_keyboard=True)
```

### **Шаг 2: Замените файл `keyboards.py`**

Замените содержимое файла `keyboards.py` на исправленную версию из `keyboards_windows_fixed.py`

### **Шаг 3: Проверьте обработчики**

Убедитесь, что в файле `handlers/main_menu.py` есть обработчик:

```python
@router.message(F.text == "📚 Инструкции")
async def instructions_prompt(message: types.Message, state: FSMContext):
    session = get_session(message.from_user.id)
    if not session:
        await message.answer("Сначала авторизуйтесь: /start")
        return
    # Redirect to instructions handler
    from handlers.instructions import instructions_start
    await instructions_start(message, state)
```

### **Шаг 4: Проверьте подключение роутеров**

Убедитесь, что в файле `bot.py` подключен роутер инструкций:

```python
from handlers import instructions as instructions_handlers

# В функции main():
dp.include_router(instructions_handlers.router)
```

### **Шаг 5: Перезапустите бота**

После исправления перезапустите бота:

```cmd
python bot.py
```

## 🎯 **Ожидаемый результат:**

После исправления в главном меню должно быть **4 кнопки**:

1. 🛠 Helpdesk
2. 👤 Справочник сотрудников  
3. 📚 Инструкции ← **Эта кнопка должна появиться**
4. 🔧 Админ панель

## 🔍 **Проверка:**

1. Запустите бота
2. Авторизуйтесь
3. Проверьте, что в главном меню есть кнопка "📚 Инструкции"
4. Нажмите на неё - должен открыться раздел инструкций с OTP авторизацией

## 🚨 **Если кнопка все еще не появляется:**

1. Убедитесь, что файл `keyboards.py` исправлен
2. Проверьте, что бот перезапущен
3. Убедитесь, что пользователь авторизован
4. Проверьте логи бота на наличие ошибок

## 📞 **Поддержка:**

Если проблемы остаются, проверьте:
- Правильность токена бота
- Установленные зависимости
- Логи бота
- Правильность ID администратора