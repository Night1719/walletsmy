#!/usr/bin/env python3
"""
Пример скрипта мониторинга для админского портала
"""
import psutil
import json
import sys
import time
from datetime import datetime

def check_system_health():
    """Проверка состояния системы"""
    health_data = {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'status': 'healthy'
    }
    
    # Проверка пороговых значений
    if health_data['cpu_percent'] > 80:
        health_data['status'] = 'warning'
        health_data['alerts'] = ['High CPU usage']
    
    if health_data['memory_percent'] > 85:
        health_data['status'] = 'warning'
        if 'alerts' not in health_data:
            health_data['alerts'] = []
        health_data['alerts'].append('High memory usage')
    
    if health_data['disk_percent'] > 90:
        health_data['status'] = 'critical'
        if 'alerts' not in health_data:
            health_data['alerts'] = []
        health_data['alerts'].append('High disk usage')
    
    return health_data

def main():
    """Основная функция"""
    try:
        print("Starting system health check...")
        
        # Проверка состояния системы
        health_data = check_system_health()
        
        # Вывод результатов
        print(json.dumps(health_data, indent=2))
        
        # Возвращаем код выхода в зависимости от статуса
        if health_data['status'] == 'critical':
            sys.exit(2)
        elif health_data['status'] == 'warning':
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)

if __name__ == "__main__":
    main()