#!/usr/bin/env python3
"""
Fix .env file for local Mini App
"""
import os
from pathlib import Path

def fix_env_file():
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env файл не найден")
        return False
    
    # Read current .env
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Update lines
    updated_lines = []
    for line in lines:
        if line.startswith('MINIAPP_URL='):
            updated_lines.append('MINIAPP_URL=http://localhost:4477/miniapp\n')
        elif line.startswith('MINIAPP_WEBHOOK_URL='):
            updated_lines.append('MINIAPP_WEBHOOK_URL=http://localhost:4477\n')
        elif line.startswith('MINIAPP_MODE='):
            updated_lines.append('MINIAPP_MODE=local\n')
        elif line.startswith('SSL_VERIFY='):
            updated_lines.append('SSL_VERIFY=false\n')
        elif line.startswith('SSL_VERIFY_CERT='):
            updated_lines.append('SSL_VERIFY_CERT=false\n')
        elif line.startswith('SSL_VERIFY_HOSTNAME='):
            updated_lines.append('SSL_VERIFY_HOSTNAME=false\n')
        else:
            updated_lines.append(line)
    
    # Write updated .env
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    print("✅ .env файл исправлен")
    print("📋 Настройки:")
    print("   MINIAPP_URL=http://localhost:4477/miniapp")
    print("   MINIAPP_MODE=local")
    print("   SSL_VERIFY=false")
    
    return True

if __name__ == "__main__":
    print("🔧 Исправление .env файла для локального Mini App")
    print("=" * 50)
    
    if fix_env_file():
        print("\n🎉 Готово! Теперь можно запускать бота:")
        print("   python bot.py")
    else:
        print("\n❌ Ошибка исправления .env файла")