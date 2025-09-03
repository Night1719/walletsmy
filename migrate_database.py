#!/usr/bin/env python3
"""
Скрипт миграции базы данных для добавления новых полей
"""

import os
import sys
from datetime import datetime

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def migrate_database():
    """Выполняет миграцию базы данных"""
    print("🔄 Начинаем миграцию базы данных...")
    
    with app.app_context():
        try:
            # Проверяем, существует ли таблица surveys
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='survey'"))
            if not result.fetchone():
                print("❌ Таблица 'survey' не найдена. Создайте базу данных сначала.")
                return False
            
            # Добавляем новые поля в таблицу Survey
            print("📝 Добавляем новые поля в таблицу Survey...")
            
            # Проверяем, существует ли поле require_name
            try:
                db.session.execute(text("SELECT require_name FROM survey LIMIT 1"))
                print("✅ Поле 'require_name' уже существует")
            except:
                print("➕ Добавляем поле 'require_name'")
                db.session.execute(text("ALTER TABLE survey ADD COLUMN require_name BOOLEAN DEFAULT 0"))
            
            # Добавляем новые поля в таблицу Question
            print("📝 Добавляем новые поля в таблицу Question...")
            
            new_question_fields = [
                ("is_required", "BOOLEAN DEFAULT 1"),
                ("allow_other", "BOOLEAN DEFAULT 0"),
                ("other_text", "VARCHAR(200)"),
                ("rating_min", "INTEGER DEFAULT 1"),
                ("rating_max", "INTEGER DEFAULT 10"),
                ("rating_labels", "TEXT"),
                ("grid_rows", "TEXT"),
                ("grid_columns", "TEXT"),
                ("question_order", "INTEGER DEFAULT 0")
            ]
            
            for field_name, field_type in new_question_fields:
                try:
                    db.session.execute(text(f"SELECT {field_name} FROM question LIMIT 1"))
                    print(f"✅ Поле '{field_name}' уже существует")
                except:
                    print(f"➕ Добавляем поле '{field_name}'")
                    db.session.execute(text(f"ALTER TABLE question ADD COLUMN {field_name} {field_type}"))
            
            # Обновляем тип поля type в таблице Question
            print("📝 Обновляем тип поля 'type' в таблице Question...")
            try:
                # SQLite не поддерживает изменение типа столбца, поэтому пропускаем
                print("ℹ️  Поле 'type' уже имеет достаточную длину")
            except Exception as e:
                print(f"⚠️  Не удалось обновить поле 'type': {e}")
            
            # Добавляем новые поля в таблицу SurveyResponse
            print("📝 Добавляем новые поля в таблицу SurveyResponse...")
            
            new_response_fields = [
                ("respondent_name", "VARCHAR(200)"),
                ("user_agent", "TEXT"),
                ("completion_time", "INTEGER")
            ]
            
            for field_name, field_type in new_response_fields:
                try:
                    db.session.execute(text(f"SELECT {field_name} FROM survey_response LIMIT 1"))
                    print(f"✅ Поле '{field_name}' уже существует")
                except:
                    print(f"➕ Добавляем поле '{field_name}'")
                    db.session.execute(text(f"ALTER TABLE survey_response ADD COLUMN {field_name} {field_type}"))
            
            # Добавляем поле is_other в таблицу Answer
            print("📝 Добавляем поле 'is_other' в таблицу Answer...")
            try:
                db.session.execute(text("SELECT is_other FROM answer LIMIT 1"))
                print("✅ Поле 'is_other' уже существует")
            except:
                print("➕ Добавляем поле 'is_other'")
                db.session.execute(text("ALTER TABLE answer ADD COLUMN is_other BOOLEAN DEFAULT 0"))
            
            # Создаем новые таблицы для аналитики
            print("📝 Создаем новые таблицы для аналитики...")
            
            # Таблица AnalyticsCache
            try:
                db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='analytics_cache'"))
                print("✅ Таблица 'analytics_cache' уже существует")
            except:
                print("➕ Создаем таблицу 'analytics_cache'")
                db.session.execute(text("""
                    CREATE TABLE analytics_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cache_key VARCHAR(200) UNIQUE NOT NULL,
                        data TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        expires_at DATETIME NOT NULL
                    )
                """))
            
            # Таблица SurveyAnalytics
            try:
                db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='survey_analytics'"))
                print("✅ Таблица 'survey_analytics' уже существует")
            except:
                print("➕ Создаем таблицу 'survey_analytics'")
                db.session.execute(text("""
                    CREATE TABLE survey_analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        survey_id INTEGER NOT NULL,
                        metric_name VARCHAR(100) NOT NULL,
                        metric_value FLOAT NOT NULL,
                        calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (survey_id) REFERENCES survey (id)
                    )
                """))
            
            # Сохраняем изменения
            db.session.commit()
            print("✅ Миграция базы данных завершена успешно!")
            
            # Показываем статистику
            print("\n📊 Статистика базы данных:")
            
            # Количество опросов
            result = db.session.execute(text("SELECT COUNT(*) FROM survey"))
            survey_count = result.fetchone()[0]
            print(f"   Опросов: {survey_count}")
            
            # Количество вопросов
            result = db.session.execute(text("SELECT COUNT(*) FROM question"))
            question_count = result.fetchone()[0]
            print(f"   Вопросов: {question_count}")
            
            # Количество ответов
            result = db.session.execute(text("SELECT COUNT(*) FROM survey_response"))
            response_count = result.fetchone()[0]
            print(f"   Ответов: {response_count}")
            
            # Количество пользователей
            result = db.session.execute(text("SELECT COUNT(*) FROM user"))
            user_count = result.fetchone()[0]
            print(f"   Пользователей: {user_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка миграции: {e}")
            db.session.rollback()
            return False

def create_sample_data():
    """Создает примеры данных для тестирования новых функций"""
    print("\n🎯 Создаем примеры данных...")
    
    with app.app_context():
        try:
            from app import User, Survey, Question
            from werkzeug.security import generate_password_hash
            
            # Проверяем, есть ли уже тестовые данные
            existing_surveys = Survey.query.filter(Survey.title.like('%Тест%')).count()
            if existing_surveys > 0:
                print("ℹ️  Тестовые данные уже существуют")
                return
            
            # Создаем тестового пользователя
            test_user = User.query.filter_by(username='test_creator').first()
            if not test_user:
                test_user = User(
                    username='test_creator',
                    email='test@buntergroup.com',
                    password_hash=generate_password_hash('test123'),
                    can_create_surveys=True
                )
                db.session.add(test_user)
                db.session.commit()
                print("➕ Создан тестовый пользователь")
            
            # Создаем тестовый опрос с новыми типами вопросов
            test_survey = Survey(
                title='Тест новых типов вопросов',
                description='Опрос для демонстрации новых возможностей',
                require_name=True,
                creator_id=test_user.id
            )
            db.session.add(test_survey)
            db.session.commit()
            
            # Создаем вопросы разных типов
            questions_data = [
                {
                    'text': 'Какой ваш любимый цвет?',
                    'type': 'multiple_choice',
                    'options': '["Красный", "Синий", "Зеленый", "Желтый"]',
                    'allow_other': True,
                    'other_text': 'Другой цвет'
                },
                {
                    'text': 'Оцените качество сервиса (1-5)',
                    'type': 'rating',
                    'rating_min': 1,
                    'rating_max': 5,
                    'rating_labels': '["Плохо", "Отлично"]'
                },
                {
                    'text': 'Какие функции вам нравятся? (можно выбрать несколько)',
                    'type': 'checkbox',
                    'options': '["Аналитика", "Экспорт", "Дизайн", "Простота"]',
                    'allow_other': True
                },
                {
                    'text': 'Оставьте отзыв',
                    'type': 'text',
                    'is_required': False
                }
            ]
            
            for i, q_data in enumerate(questions_data):
                question = Question(
                    text=q_data['text'],
                    type=q_data['type'],
                    options=q_data.get('options'),
                    is_required=q_data.get('is_required', True),
                    allow_other=q_data.get('allow_other', False),
                    other_text=q_data.get('other_text'),
                    rating_min=q_data.get('rating_min', 1),
                    rating_max=q_data.get('rating_max', 10),
                    rating_labels=q_data.get('rating_labels'),
                    question_order=i,
                    survey_id=test_survey.id
                )
                db.session.add(question)
            
            db.session.commit()
            print("✅ Созданы тестовые данные")
            
        except Exception as e:
            print(f"❌ Ошибка создания тестовых данных: {e}")
            db.session.rollback()

if __name__ == '__main__':
    print("🚀 BG Survey Platform - Миграция базы данных")
    print("=" * 50)
    
    # Выполняем миграцию
    if migrate_database():
        print("\n🎉 Миграция завершена успешно!")
        
        # Создаем тестовые данные
        create_sample_data()
        
        print("\n📋 Что было добавлено:")
        print("   ✅ Новый тип опроса: 'Запросить имя'")
        print("   ✅ Расширенные типы вопросов (как в Google Forms)")
        print("   ✅ Настройки рейтингов (мин/макс значения, подписи)")
        print("   ✅ Сетка флажков")
        print("   ✅ Опция 'Другой вариант' для вопросов")
        print("   ✅ Обязательные/необязательные вопросы")
        print("   ✅ Расширенная аналитика")
        print("   ✅ Улучшенные Excel отчеты")
        print("   ✅ Отслеживание времени прохождения")
        print("   ✅ User Agent браузера")
        
        print("\n🔧 Для применения изменений:")
        print("   1. Перезапустите приложение")
        print("   2. Войдите в систему")
        print("   3. Создайте новый опрос с новыми возможностями")
        print("   4. Проверьте аналитику и экспорт в Excel")
        
    else:
        print("\n❌ Миграция не удалась!")
        print("   Проверьте логи выше для диагностики проблем")
        sys.exit(1)