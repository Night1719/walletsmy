#!/usr/bin/env python3
"""
Production script for Telegram Mini App with secure links.
Configured for internet access with dynamic link generation.
"""
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))

from app import app

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s'
    )
    
    # Get configuration from environment
    host = os.getenv('MINIAPP_HOST', '0.0.0.0')
    port = int(os.getenv('MINIAPP_PORT', '5000'))
    debug = os.getenv('MINIAPP_DEBUG', 'false').lower() == 'true'
    
    # Security settings
    secret_key = os.getenv('FLASK_SECRET_KEY')
    if not secret_key:
        print("ERROR: FLASK_SECRET_KEY is required for production")
        sys.exit(1)
    
    link_expiry = int(os.getenv('LINK_EXPIRY_MINUTES', '40'))
    
    print(f"🚀 Starting Production Mini App")
    print(f"🌐 Host: {host}:{port}")
    print(f"🔒 Secure links expire in: {link_expiry} minutes")
    print(f"🐛 Debug mode: {debug}")
    print(f"🔑 Secret key configured: {'Yes' if secret_key else 'No'}")
    print()
    
    if not debug:
        print("⚠️  WARNING: Running in production mode")
        print("   Make sure to:")
        print("   - Use HTTPS in production")
        print("   - Set strong FLASK_SECRET_KEY")
        print("   - Configure proper firewall rules")
        print("   - Use reverse proxy (nginx)")
        print()
    
    app.run(host=host, port=port, debug=debug)