#!/usr/bin/env python3
"""
Пример скрипта резервного копирования для админского портала
"""
import os
import shutil
import json
import sys
from datetime import datetime
from pathlib import Path

def create_backup(source_dir, backup_dir):
    """Создание резервной копии директории"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}"
    backup_path = os.path.join(backup_dir, backup_name)
    
    try:
        # Создание директории для бэкапа
        os.makedirs(backup_path, exist_ok=True)
        
        # Копирование файлов
        if os.path.exists(source_dir):
            shutil.copytree(source_dir, os.path.join(backup_path, "data"))
            print(f"Backup created successfully: {backup_path}")
            return {
                'status': 'success',
                'backup_path': backup_path,
                'timestamp': datetime.now().isoformat()
            }
        else:
            print(f"Source directory not found: {source_dir}")
            return {
                'status': 'error',
                'message': f"Source directory not found: {source_dir}",
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        print(f"Backup failed: {e}")
        return {
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }

def cleanup_old_backups(backup_dir, keep_count=5):
    """Удаление старых резервных копий"""
    try:
        backup_files = []
        for item in os.listdir(backup_dir):
            item_path = os.path.join(backup_dir, item)
            if os.path.isdir(item_path) and item.startswith('backup_'):
                backup_files.append((item_path, os.path.getctime(item_path)))
        
        # Сортируем по дате создания (новые первыми)
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        # Удаляем старые бэкапы
        for backup_path, _ in backup_files[keep_count:]:
            shutil.rmtree(backup_path)
            print(f"Removed old backup: {backup_path}")
            
        return {
            'status': 'success',
            'cleaned_count': len(backup_files) - keep_count
        }
        
    except Exception as e:
        print(f"Cleanup failed: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def main():
    """Основная функция"""
    try:
        # Параметры по умолчанию
        source_dir = sys.argv[1] if len(sys.argv) > 1 else "/tmp"
        backup_dir = sys.argv[2] if len(sys.argv) > 2 else "/tmp/backups"
        
        print(f"Creating backup from {source_dir} to {backup_dir}")
        
        # Создание бэкапа
        result = create_backup(source_dir, backup_dir)
        print(json.dumps(result, indent=2))
        
        # Очистка старых бэкапов
        cleanup_result = cleanup_old_backups(backup_dir)
        print(f"Cleanup result: {cleanup_result}")
        
        # Возвращаем код выхода
        if result['status'] == 'success':
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)

if __name__ == "__main__":
    main()