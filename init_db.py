#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для инициализации базы данных BG Survey Platform
Создает таблицы и базовые данные
"""

import os
import sys
from datetime import datetime

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_database():
    """Инициализация базы данных"""
    
    print("=" * 60)
    print("BG Survey Platform - Инициализация базы данных")
    print("=" * 60)
    print()
    
    try:
        # Импортируем приложение и модели
        from app import app, db, User, Survey, Question
        
        with app.app_context():
            print("🔧 Создание таблиц базы данных...")
            
            # Создаем все таблицы
            db.create_all()
            print("✅ Таблицы созданы успешно")
            
            # Проверяем, есть ли уже пользователи
            if User.query.first():
                print("ℹ️  База данных уже содержит данные")
                return
            
            print("👤 Создание базовых пользователей...")
            
            # Создаем администратора по умолчанию
            from werkzeug.security import generate_password_hash
            
            admin = User(
                username='admin',
                email='admin@buntergroup.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                can_create_surveys=True,
                created_at=datetime.utcnow()
            )
            db.session.add(admin)
            
            # Создаем тестового пользователя
            test_user = User(
                username='test_user',
                email='test@buntergroup.com',
                password_hash=generate_password_hash('test123'),
                is_admin=False,
                can_create_surveys=True,
                created_at=datetime.utcnow()
            )
            db.session.add(test_user)
            
            # Создаем обычного пользователя
            regular_user = User(
                username='user',
                email='user@buntergroup.com',
                password_hash=generate_password_hash('user123'),
                is_admin=False,
                can_create_surveys=False,
                created_at=datetime.utcnow()
            )
            db.session.add(regular_user)
            
            # Сохраняем пользователей
            db.session.commit()
            print("✅ Базовые пользователи созданы")
            
            print("📊 Создание демо-опроса...")
            
            # Создаем демо-опрос
            demo_survey = Survey(
                title='Демонстрационный опрос',
                description='Этот опрос создан для демонстрации возможностей платформы',
                is_anonymous=True,
                require_auth=False,
                creator_id=admin.id,
                created_at=datetime.utcnow()
            )
            db.session.add(demo_survey)
            db.session.commit()
            
            # Создаем вопросы для демо-опроса
            questions_data = [
                {
                    'text': 'Как вы оцениваете удобство использования платформы?',
                    'type': 'rating',
                    'options': '[]'
                },
                {
                    'text': 'Какой тип опросов вы используете чаще всего?',
                    'type': 'multiple_choice',
                    'options': '["Оценка удовлетворенности", "Маркетинговые исследования", "Внутренние опросы", "Другое"]'
                },
                {
                    'text': 'Какие функции вы хотели бы видеть в будущих версиях?',
                    'type': 'text',
                    'options': '[]'
                }
            ]
            
            for q_data in questions_data:
                question = Question(
                    text=q_data['text'],
                    type=q_data['type'],
                    options=q_data['options'],
                    survey_id=demo_survey.id
                )
                db.session.add(question)
            
            db.session.commit()
            print("✅ Демо-опрос создан")
            
            print()
            print("🎉 Инициализация базы данных завершена успешно!")
            print()
            print("📋 Созданные пользователи:")
            print(f"   👑 Администратор: admin / admin123")
            print(f"   🔧 Тестовый пользователь: test_user / test123")
            print(f"   👤 Обычный пользователь: user / user123")
            print()
            print("📊 Демо-опрос доступен по адресу:")
            print(f"   http://localhost:5000/surveys/{demo_survey.id}")
            print()
            print("⚠️  ВНИМАНИЕ: Измените пароли по умолчанию в продакшене!")
            
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь, что вы находитесь в корневой директории проекта")
        print("и что все зависимости установлены.")
        return False
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        print("Проверьте логи для получения дополнительной информации.")
        return False
    
    return True

def reset_database():
    """Сброс базы данных (удаление всех данных)"""
    
    print("=" * 60)
    print("BG Survey Platform - Сброс базы данных")
    print("=" * 60)
    print()
    
    confirm = input("⚠️  ВНИМАНИЕ: Это действие удалит ВСЕ данные! Продолжить? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("❌ Операция отменена")
        return False
    
    try:
        from app import app, db
        
        with app.app_context():
            print("🗑️  Удаление всех таблиц...")
            db.drop_all()
            print("✅ Таблицы удалены")
            
            print("🔧 Создание новых таблиц...")
            db.create_all()
            print("✅ Таблицы созданы заново")
            
            print("🎉 База данных сброшена успешно!")
            
    except Exception as e:
        print(f"❌ Ошибка сброса: {e}")
        return False
    
    return True

def show_database_info():
    """Показать информацию о базе данных"""
    
    print("=" * 60)
    print("BG Survey Platform - Информация о базе данных")
    print("=" * 60)
    print()
    
    try:
        from app import app, db, User, Survey, Question
        
        with app.app_context():
            # Информация о пользователях
            users = User.query.all()
            print(f"👥 Пользователи: {len(users)}")
            for user in users:
                roles = []
                if user.is_admin:
                    roles.append("Админ")
                if user.can_create_surveys:
                    roles.append("Создает опросы")
                if not roles:
                    roles.append("Базовые права")
                
                print(f"   • {user.username} ({user.email}) - {', '.join(roles)}")
            
            print()
            
            # Информация об опросах
            surveys = Survey.query.all()
            print(f"📊 Опросы: {len(surveys)}")
            for survey in surveys:
                creator = User.query.get(survey.creator_id)
                questions_count = Question.query.filter_by(survey_id=survey.id).count()
                print(f"   • {survey.title} - {questions_count} вопросов (создатель: {creator.username if creator else 'Неизвестно'})")
            
            print()
            
            # Общая статистика
            total_questions = Question.query.count()
            print(f"📝 Всего вопросов: {total_questions}")
            
    except Exception as e:
        print(f"❌ Ошибка получения информации: {e}")
        return False
    
    return True

def main():
    """Основная функция"""
    
    print("BG Survey Platform - Инструмент управления базой данных")
    print("Выберите действие:")
    print("1. Инициализировать базу данных")
    print("2. Сбросить базу данных")
    print("3. Показать информацию о базе данных")
    print("4. Выход")
    print()
    
    while True:
        choice = input("Введите номер (1-4): ").strip()
        
        if choice == '1':
            success = init_database()
            break
        elif choice == '2':
            success = reset_database()
            break
        elif choice == '3':
            success = show_database_info()
            break
        elif choice == '4':
            print("Выход...")
            return
        else:
            print("❌ Неверный выбор. Введите число от 1 до 4.")
    
    print()
    print("=" * 60)
    if success:
        print("✅ Операция выполнена успешно!")
    else:
        print("❌ Операция завершилась с ошибкой")
    print("=" * 60)

if __name__ == '__main__':
    main()