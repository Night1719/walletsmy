.PHONY: help install test run run-worker run-sniper docker-up docker-down docker-build clean

help: ## Показать справку
	@echo "Solana Trading Bot - Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

install-dev: ## Установить зависимости для разработки
	pip install -r requirements-dev.txt

test: ## Запустить тесты
	pytest tests/ -v

test-cov: ## Запустить тесты с coverage
	pytest tests/ --cov=app --cov=bot --cov-report=html

lint: ## Проверить код линтером
	black app/ bot/ worker/ tests/
	isort app/ bot/ worker/ tests/
	flake8 app/ bot/ worker/ tests/

format: ## Отформатировать код
	black app/ bot/ worker/ tests/
	isort app/ bot/ worker/ tests/

run: ## Запустить FastAPI приложение
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-worker: ## Запустить Celery worker
	celery -A worker.celery_app worker --loglevel=info

run-sniper: ## Запустить Sniper Bot
	python run_sniper.py

docker-up: ## Запустить все сервисы через Docker
	docker-compose up -d

docker-down: ## Остановить все сервисы Docker
	docker-compose down

docker-build: ## Собрать Docker образы
	docker-compose build

docker-logs: ## Показать логи Docker
	docker-compose logs -f

db-init: ## Инициализировать базу данных
	alembic upgrade head

db-migrate: ## Создать новую миграцию
	@read -p "Enter migration description: " desc; \
	alembic revision --autogenerate -m "$$desc"

db-upgrade: ## Применить миграции
	alembic upgrade head

db-downgrade: ## Откатить миграции
	alembic downgrade -1

clean: ## Очистить временные файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

setup: ## Полная настройка проекта
	@echo "Настройка Solana Trading Bot..."
	make install
	make db-init
	@echo "Настройка завершена!"

dev-setup: ## Настройка для разработки
	@echo "Настройка для разработки..."
	make install-dev
	make db-init
	@echo "Настройка для разработки завершена!"

status: ## Показать статус сервисов
	@echo "Статус сервисов:"
	@docker-compose ps
	@echo ""
	@echo "Логи последних ошибок:"
	@docker-compose logs --tail=10 | grep -i error || echo "Ошибок не найдено"

monitor: ## Открыть мониторинг в браузере
	@echo "Открытие мониторинга..."
	@echo "Grafana: http://localhost:3000 (admin/admin)"
	@echo "Prometheus: http://localhost:9090"
	@echo "FastAPI: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"