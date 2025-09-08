# Настройка Telegram Mini App для Windows

## 🖥️ Системные требования

- **Windows 10/11** (64-bit)
- **Python 3.8+** (скачать с [python.org](https://python.org))
- **PowerShell 5.1+** (встроен в Windows 10/11)
- **Интернет** (только для первоначальной установки)

## 🚀 Быстрый запуск

### 1. Подготовка файлов

1. **Скопируйте папку `miniapp`** на ваш компьютер
2. **Создайте папку `local_files`** внутри `miniapp`
3. **Поместите файлы инструкций** в папку `local_files`:

```
miniapp/
├── local_files/
│   ├── 1c_ar2.pdf
│   ├── 1c_ar2.docx
│   ├── 1c_dm.pdf
│   ├── 1c_dm.docx
│   ├── email_iphone.pdf
│   ├── email_iphone.docx
│   ├── email_android.pdf
│   ├── email_android.docx
│   ├── email_outlook.pdf
│   └── email_outlook.docx
```

### 2. Запуск через PowerShell

1. **Откройте PowerShell** от имени администратора
2. **Перейдите в папку miniapp**:
   ```powershell
   cd C:\path\to\miniapp
   ```
3. **Запустите скрипт**:
   ```powershell
   .\run_windows.ps1
   ```

### 3. Запуск через командную строку

1. **Откройте командную строку** (cmd)
2. **Перейдите в папку miniapp**:
   ```cmd
   cd C:\path\to\miniapp
   ```
3. **Запустите bat-файл**:
   ```cmd
   run_windows.bat
   ```

## ⚙️ Настройка

### 1. Настройка переменных окружения

Создайте файл `.env` в папке `miniapp`:

```env
# Telegram Bot Token
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Mini App Configuration
MINIAPP_URL=http://localhost:5000/miniapp
MINIAPP_MODE=local
FLASK_SECRET_KEY=your_secret_key_here

# File Server (если нужен)
FILE_SERVER_BASE_URL=https://files.example.com
FILE_SERVER_USER=your_file_server_user
FILE_SERVER_PASS=your_file_server_password
```

### 2. Настройка бота

В файле `config.py` бота установите:

```python
MINIAPP_URL = "http://localhost:5000/miniapp"
MINIAPP_MODE = "local"
```

### 3. Настройка файлов инструкций

Поместите файлы в папку `local_files` с правильными именами:

| Тип инструкции | PDF файл | Word файл |
|----------------|----------|-----------|
| 1С AR2 | `1c_ar2.pdf` | `1c_ar2.docx` |
| 1С DM | `1c_dm.pdf` | `1c_dm.docx` |
| iPhone | `email_iphone.pdf` | `email_iphone.docx` |
| Android | `email_android.pdf` | `email_android.docx` |
| Outlook | `email_outlook.pdf` | `email_outlook.docx` |

## 🔧 Ручная установка

### 1. Установка Python

1. Скачайте Python с [python.org](https://python.org)
2. **ВАЖНО**: При установке отметьте "Add Python to PATH"
3. Перезагрузите компьютер

### 2. Установка зависимостей

```cmd
cd C:\path\to\miniapp
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Запуск приложения

```cmd
python run.py
```

## 🌐 Настройка бота для локального Mini App

### 1. Обновление конфигурации бота

В файле `config.py`:

```python
# === Telegram Mini App ===
MINIAPP_URL = "http://localhost:5000/miniapp"
MINIAPP_MODE = "local"
```

### 2. Настройка BotFather

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Выберите вашего бота
3. Выберите "Bot Settings" → "Mini App"
4. Установите URL: `http://localhost:5000/miniapp`

**⚠️ ВАЖНО**: Для локального Mini App нужен ngrok или аналогичный туннель!

### 3. Использование ngrok для туннеля

1. **Скачайте ngrok** с [ngrok.com](https://ngrok.com)
2. **Запустите ngrok**:
   ```cmd
   ngrok http 5000
   ```
3. **Скопируйте HTTPS URL** (например: `https://abc123.ngrok.io`)
4. **Установите в BotFather**: `https://abc123.ngrok.io/miniapp`

## 📱 Тестирование

### 1. Проверка Mini App

1. Откройте браузер
2. Перейдите на `http://localhost:5000/miniapp`
3. Должна открыться страница с инструкциями

### 2. Тестирование в Telegram

1. Запустите бота
2. Отправьте команду `/start`
3. Перейдите в "📚 Инструкции"
4. Выберите тип инструкции
5. Нажмите "📚 Открыть инструкции"

## 🔧 Устранение неполадок

### Проблема: "Python не найден"

**Решение:**
1. Переустановите Python с отметкой "Add Python to PATH"
2. Перезагрузите компьютер
3. Проверьте: `python --version`

### Проблема: "Модуль не найден"

**Решение:**
```cmd
pip install -r requirements.txt
```

### Проблема: "Файлы не найдены"

**Решение:**
1. Проверьте папку `local_files`
2. Убедитесь в правильности имен файлов
3. Проверьте права доступа к файлам

### Проблема: "Mini App не открывается"

**Решение:**
1. Проверьте, что сервер запущен на порту 5000
2. Проверьте URL в BotFather
3. Используйте ngrok для туннеля

### Проблема: "PDF не отображается"

**Решение:**
1. Проверьте, что PDF файл не поврежден
2. Попробуйте другой PDF файл
3. Проверьте консоль браузера на ошибки

## 📊 Мониторинг

### Просмотр логов

```cmd
# В PowerShell
Get-Content -Path "app.log" -Wait

# В командной строке
type app.log
```

### Проверка статуса

```cmd
# Проверка порта
netstat -an | findstr :5000

# Проверка процессов
tasklist | findstr python
```

## 🚀 Автозапуск

### 1. Создание задачи Windows

1. Откройте "Планировщик заданий"
2. Создайте новую задачу
3. Установите запуск при старте системы
4. Укажите путь к `run_windows.bat`

### 2. Создание ярлыка

1. Создайте ярлык для `run_windows.bat`
2. Поместите в папку "Автозагрузка"
3. Установите запуск от имени администратора

## ✅ Итог

**Для запуска Mini App на Windows нужно:**

1. ✅ **Установить Python 3.8+**
2. ✅ **Скопировать файлы miniapp**
3. ✅ **Поместить файлы инструкций в local_files**
4. ✅ **Запустить run_windows.bat или run_windows.ps1**
5. ✅ **Настроить ngrok для туннеля**
6. ✅ **Обновить URL в BotFather**

**Mini App будет работать локально без интернета!** 🎉