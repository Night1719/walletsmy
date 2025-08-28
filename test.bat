@echo off
echo Тест системы...
echo.

echo 1. Проверка Python...
python --version
echo.

echo 2. Проверка файлов...
if exist "manage.py" (
    echo manage.py найден
) else (
    echo manage.py НЕ найден!
)

if exist "requirements.txt" (
    echo requirements.txt найден
) else (
    echo requirements.txt НЕ найден!
)

if exist "venv" (
    echo venv найден
) else (
    echo venv НЕ найден!
)
echo.

echo 3. Текущая папка:
cd
echo.

echo 4. Содержимое папки:
dir
echo.

echo Тест завершен. Нажмите любую клавишу...
pause >nul