#!/usr/bin/env python3
"""
Пример скрипта обслуживания для админского портала
"""
import os
import shutil
import json
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def cleanup_temp_files(temp_dirs, max_age_days=7):
    """Очистка временных файлов старше указанного количества дней"""
    cleaned_files = []
    total_size = 0
    cutoff_time = datetime.now() - timedelta(days=max_age_days)
    
    for temp_dir in temp_dirs:
        if not os.path.exists(temp_dir):
            continue
            
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    if file_time < cutoff_time:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        cleaned_files.append(file_path)
                        total_size += file_size
                except (OSError, PermissionError):
                    # Пропускаем файлы, которые не можем удалить
                    pass
    
    return {
        'cleaned_files': len(cleaned_files),
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'files': cleaned_files[:10]  # Показываем только первые 10 файлов
    }

def check_disk_space(path="/", min_free_gb=5):
    """Проверка свободного места на диске"""
    statvfs = os.statvfs(path)
    free_bytes = statvfs.f_frsize * statvfs.f_bavail
    free_gb = free_bytes / (1024**3)
    
    return {
        'free_gb': round(free_gb, 2),
        'min_required_gb': min_free_gb,
        'status': 'ok' if free_gb >= min_free_gb else 'warning'
    }

def update_system_packages():
    """Обновление системных пакетов (для Ubuntu/Debian)"""
    try:
        # Проверяем доступность apt
        result = subprocess.run(['which', 'apt'], capture_output=True, text=True)
        if result.returncode != 0:
            return {'status': 'skipped', 'message': 'apt not available'}
        
        # Получаем список обновлений
        result = subprocess.run(['apt', 'list', '--upgradable'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            upgradable_packages = [line for line in result.stdout.split('\n') 
                                 if line and not line.startswith('Listing...')]
            return {
                'status': 'success',
                'upgradable_count': len(upgradable_packages),
                'packages': upgradable_packages[:10]  # Показываем первые 10
            }
        else:
            return {'status': 'error', 'message': result.stderr}
            
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def restart_services(services):
    """Перезапуск сервисов"""
    results = []
    
    for service in services:
        try:
            result = subprocess.run(['systemctl', 'restart', service], 
                                  capture_output=True, text=True)
            results.append({
                'service': service,
                'status': 'success' if result.returncode == 0 else 'failed',
                'message': result.stderr if result.returncode != 0 else 'Restarted successfully'
            })
        except Exception as e:
            results.append({
                'service': service,
                'status': 'error',
                'message': str(e)
            })
    
    return results

def main():
    """Основная функция обслуживания"""
    try:
        maintenance_results = {
            'timestamp': datetime.now().isoformat(),
            'tasks': {}
        }
        
        print("Starting system maintenance...")
        
        # Очистка временных файлов
        print("Cleaning temporary files...")
        temp_dirs = ['/tmp', '/var/tmp', '/tmp/systemd-private-*']
        cleanup_result = cleanup_temp_files(temp_dirs)
        maintenance_results['tasks']['cleanup'] = cleanup_result
        print(f"Cleaned {cleanup_result['cleaned_files']} files, "
              f"freed {cleanup_result['total_size_mb']} MB")
        
        # Проверка места на диске
        print("Checking disk space...")
        disk_result = check_disk_space()
        maintenance_results['tasks']['disk_check'] = disk_result
        print(f"Free disk space: {disk_result['free_gb']} GB")
        
        # Проверка обновлений пакетов
        print("Checking for package updates...")
        update_result = update_system_packages()
        maintenance_results['tasks']['updates'] = update_result
        if update_result['status'] == 'success':
            print(f"Found {update_result['upgradable_count']} upgradable packages")
        
        # Перезапуск сервисов (опционально)
        services_to_restart = []  # Добавьте сервисы для перезапуска
        if services_to_restart:
            print("Restarting services...")
            restart_result = restart_services(services_to_restart)
            maintenance_results['tasks']['service_restart'] = restart_result
        
        # Вывод результатов
        print("\nMaintenance completed:")
        print(json.dumps(maintenance_results, indent=2))
        
        # Определяем общий статус
        has_errors = any(
            task.get('status') == 'error' 
            for task in maintenance_results['tasks'].values()
        )
        
        sys.exit(1 if has_errors else 0)
        
    except Exception as e:
        print(f"Maintenance failed: {e}", file=sys.stderr)
        sys.exit(3)

if __name__ == "__main__":
    main()