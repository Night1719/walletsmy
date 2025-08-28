#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания первого администратора BG Survey Platform
Используйте этот скрипт для первоначальной настройки системы
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_admin():
    """Создание администратора системы"""
    
    print("=" * 50)
    print("BG Survey Platform - Создание администратора")
    print("=" * 50)
    print()
    
    try:
        # Импортируем приложение и модели
        from app import app, db, User
        
        with app.app_context():
            # Проверяем, есть ли уже администраторы
            existing_admin = User.query.filter_by(is_admin=True).first()
            if existing_admin:
                print(f"✅ Администратор уже существует: {existing_admin.username}")
                print(f"   Email: {existing_admin.email}")
                print(f"   ID: {existing_admin.id}")
                return
            
            print("Создание первого администратора системы...")
            print()
            
            # Запрашиваем данные администратора
            username = input("Введите имя пользователя (по умолчанию: admin): ").strip()
            if not username:
                username = "admin"
            
            email = input("Введите email (по умолчанию: admin@buntergroup.com): ").strip()
            if not email:
                email = "admin@buntergroup.com"
            
            password = input("Введите пароль (по умолчанию: admin123): ").strip()
            if not password:
                password = "admin123"
            
            # Проверяем, не существует ли пользователь с таким именем
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"❌ Пользователь с именем '{username}' уже существует!")
                return
            
            # Проверяем, не существует ли пользователь с таким email
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                print(f"❌ Пользователь с email '{email}' уже существует!")
                return
            
            # Создаем администратора
            admin = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                is_admin=True,
                can_create_surveys=True
            )
            
            # Добавляем в базу данных
            db.session.add(admin)
            db.session.commit()
            
            print()
            print("✅ Администратор успешно создан!")
            print(f"   Имя пользователя: {username}")
            print(f"   Email: {email}")
            print(f"   ID: {admin.id}")
            print()
            print("Теперь вы можете войти в систему с этими учетными данными")
            print("и получить доступ к админ панели.")
            
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь, что вы находитесь в корневой директории проекта")
        print("и что все зависимости установлены.")
        return
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("Проверьте логи для получения дополнительной информации.")
        return

def create_test_user():
    """Создание тестового пользователя с правами на создание опросов"""
    
    print()
    print("=" * 50)
    print("Создание тестового пользователя")
    print("=" * 50)
    print()
    
    try:
        from app import app, db, User
        
        with app.app_context():
            # Проверяем, есть ли уже тестовый пользователь
            existing_user = User.query.filter_by(username='test_user').first()
            if existing_user:
                print("✅ Тестовый пользователь уже существует")
                return
            
            print("Создание тестового пользователя...")
            
            # Создаем тестового пользователя
            test_user = User(
                username='test_user',
                email='test@buntergroup.com',
                password_hash=generate_password_hash('test123'),
                is_admin=False,
                can_create_surveys=True
            )
            
            # Добавляем в базу данных
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Тестовый пользователь создан!")
            print(f"   Имя пользователя: test_user")
            print(f"   Пароль: test123")
            print(f"   Может создавать опросы: Да")
            
    except Exception as e:
        print(f"❌ Ошибка создания тестового пользователя: {e}")

def main():
    """Основная функция"""
    
    print("BG Survey Platform - Инструмент настройки")
    print("Выберите действие:")
    print("1. Создать администратора")
    print("2. Создать тестового пользователя")
    print("3. Создать и администратора, и тестового пользователя")
    print("4. Выход")
    print()
    
    while True:
        choice = input("Введите номер (1-4): ").strip()
        
        if choice == '1':
            create_admin()
            break
        elif choice == '2':
            create_test_user()
            break
        elif choice == '3':
            create_admin()
            create_test_user()
            break
        elif choice == '4':
            print("Выход...")
            break
        else:
            print("❌ Неверный выбор. Введите число от 1 до 4.")
    
    print()
    print("=" * 50)
    print("Настройка завершена!")
    print("=" * 50)

if __name__ == '__main__':
    main()