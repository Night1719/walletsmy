#!/usr/bin/env python3
"""
Certificate Installation Script for Mini App
Allows installing SSL certificate from text input
"""
import os
import sys
from pathlib import Path
import tempfile
import shutil

def create_certificate_files(cert_text, key_text=None, password=None):
    """Create certificate files from text input"""
    
    # Create certificates directory
    cert_dir = Path(__file__).parent / "certificates"
    cert_dir.mkdir(exist_ok=True)
    
    # Certificate file
    cert_file = cert_dir / "server.crt"
    with open(cert_file, 'w', encoding='utf-8') as f:
        f.write(cert_text)
    
    print(f"✅ Certificate saved to: {cert_file}")
    
    # Private key file (if provided)
    key_file = None
    if key_text:
        key_file = cert_dir / "server.key"
        with open(key_file, 'w', encoding='utf-8') as f:
            f.write(key_text)
        print(f"✅ Private key saved to: {key_file}")
    
    # Password file (if provided)
    password_file = None
    if password:
        password_file = cert_dir / "password.txt"
        with open(password_file, 'w', encoding='utf-8') as f:
            f.write(password)
        print(f"✅ Password saved to: {password_file}")
    
    return cert_file, key_file, password_file

def update_env_file(cert_file, key_file=None, password_file=None):
    """Update .env file with certificate paths"""
    
    env_file = Path(__file__).parent / ".env"
    
    # Read current .env content
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Update or add SSL configuration
    ssl_config = {
        'SSL_VERIFY': 'true',
        'SSL_VERIFY_CERT': 'true',
        'SSL_VERIFY_HOSTNAME': 'true',
        'SSL_CERT_PATH': str(cert_file),
    }
    
    if key_file:
        ssl_config['SSL_KEY_PATH'] = str(key_file)
    
    if password_file:
        ssl_config['SSL_PASSWORD'] = str(password_file)
    
    # Update existing lines or add new ones
    updated_lines = []
    ssl_section_found = False
    
    for line in lines:
        if line.startswith('# === SSL Configuration ==='):
            ssl_section_found = True
            updated_lines.append(line)
            # Add SSL config
            for key, value in ssl_config.items():
                updated_lines.append(f"{key}={value}\n")
        elif line.startswith('SSL_'):
            # Skip old SSL lines
            continue
        else:
            updated_lines.append(line)
    
    # If SSL section not found, add it
    if not ssl_section_found:
        updated_lines.append('\n# === SSL Configuration ===\n')
        for key, value in ssl_config.items():
            updated_lines.append(f"{key}={value}\n")
    
    # Write updated .env
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    print(f"✅ .env file updated: {env_file}")

def validate_certificate(cert_file):
    """Validate certificate file"""
    try:
        import ssl
        import socket
        
        # Read certificate
        with open(cert_file, 'r') as f:
            cert_data = f.read()
        
        # Check if it's a valid PEM certificate
        if '-----BEGIN CERTIFICATE-----' not in cert_data:
            print("❌ Invalid certificate format. Expected PEM format.")
            return False
        
        # Try to parse certificate
        import base64
        import binascii
        
        # Extract certificate content
        cert_lines = []
        in_cert = False
        for line in cert_data.split('\n'):
            if '-----BEGIN CERTIFICATE-----' in line:
                in_cert = True
                continue
            elif '-----END CERTIFICATE-----' in line:
                break
            elif in_cert:
                cert_lines.append(line)
        
        if not cert_lines:
            print("❌ No certificate content found")
            return False
        
        # Decode base64
        try:
            cert_der = base64.b64decode(''.join(cert_lines))
            print("✅ Certificate format is valid")
            return True
        except Exception as e:
            print(f"❌ Certificate decoding failed: {e}")
            return False
            
    except ImportError:
        print("⚠️  SSL module not available, skipping validation")
        return True
    except Exception as e:
        print(f"❌ Certificate validation failed: {e}")
        return False

def main():
    print("🔐 SSL Certificate Installation for Mini App")
    print("=" * 50)
    
    # Get certificate text
    print("\n📋 Paste your SSL certificate (PEM format):")
    print("   (Include -----BEGIN CERTIFICATE----- and -----END CERTIFICATE-----)")
    print("   (Press Ctrl+Z and Enter when done on Windows, Ctrl+D on Linux/Mac)")
    print()
    
    cert_lines = []
    try:
        while True:
            line = input()
            cert_lines.append(line)
    except EOFError:
        pass
    
    cert_text = '\n'.join(cert_lines)
    
    if not cert_text.strip():
        print("❌ No certificate provided")
        return 1
    
    # Validate certificate
    if not validate_certificate_text(cert_text):
        print("❌ Invalid certificate format")
        return 1
    
    # Get private key (optional)
    print("\n🔑 Private key (optional, press Enter to skip):")
    print("   (Include -----BEGIN PRIVATE KEY----- and -----END PRIVATE KEY-----)")
    
    key_lines = []
    try:
        while True:
            line = input()
            if not line.strip():  # Empty line means done
                break
            key_lines.append(line)
    except EOFError:
        pass
    
    key_text = '\n'.join(key_lines) if key_lines else None
    
    # Get password (optional)
    password = None
    if key_text:
        print("\n🔐 Certificate password (optional, press Enter to skip):")
        password = input().strip() or None
    
    # Create certificate files
    try:
        cert_file, key_file, password_file = create_certificate_files(cert_text, key_text, password)
        
        # Update .env file
        update_env_file(cert_file, key_file, password_file)
        
        print("\n✅ Certificate installation completed!")
        print("\n📁 Files created:")
        print(f"   Certificate: {cert_file}")
        if key_file:
            print(f"   Private key: {key_file}")
        if password_file:
            print(f"   Password: {password_file}")
        
        print("\n🚀 You can now run Mini App with SSL:")
        print("   python run.py")
        print("   or")
        print("   run_ssl.bat")
        
        return 0
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return 1

def validate_certificate_text(cert_text):
    """Validate certificate text format"""
    cert_text = cert_text.strip()
    
    if not cert_text:
        return False
    
    # Check for PEM format markers
    if '-----BEGIN CERTIFICATE-----' not in cert_text:
        return False
    
    if '-----END CERTIFICATE-----' not in cert_text:
        return False
    
    return True

if __name__ == "__main__":
    sys.exit(main())