# Windows: Установка и запуск Solana DEX Trading Bot

## Предварительные требования
- Windows 10/11 (PowerShell 5.1+ или PowerShell 7)
- Администраторские права (для установки и служб)
- Python 3.9+ и Git (установятся через скрипт при необходимости)
- Docker Desktop (рекомендуется для PostgreSQL/Redis)

## Варианты установки

### Вариант A: Автоматическая установка (PowerShell)
```powershell
# Открыть PowerShell от имени администратора
Set-ExecutionPolicy RemoteSigned -Scope Process -Force
./windows/install.ps1
```

Что делает install.ps1:
- Проверяет среду, при необходимости предлагает установить Chocolatey
- Устанавливает Python/Git/NSSM (по запросу)
- Поднимает PostgreSQL и Redis через Docker Desktop
- Создаёт venv, ставит зависимости, копирует .env
- Применяет миграции Alembic
- Создаёт папку logs

### Вариант B: Docker Compose (все сервисы)
```powershell
# Запуск всех контейнеров
docker compose up -d

# Логи
docker compose logs -f
```

### Вариант C: Ручной запуск (локальный Python + Docker для БД)
```powershell
# БД и Redis в Docker
docker compose up -d postgres redis

# Виртуальное окружение
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt
alembic upgrade head

# Запуск компонентов
./windows/run_all.ps1
```

## Быстрый старт (Windows)
```powershell
Set-ExecutionPolicy RemoteSigned -Scope Process -Force
./windows/install.ps1
./windows/health_check.ps1
./windows/run_all.ps1
```

## Управление как службами Windows (через NSSM)
```powershell
# Установка служб
./windows/setup_services.ps1

# Удаление служб
./windows/uninstall_services.ps1
```

## Health-check
```powershell
./windows/health_check.ps1
```

## Полезные ссылки
- Основная документация: README.md, INSTALL.md, USER_GUIDE.md
- Быстрый старт: QUICKSTART.md
- Примеры: EXAMPLES.md