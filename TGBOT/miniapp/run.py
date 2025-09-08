#!/usr/bin/env python3
"""
Script to run the Telegram Mini App for instruction viewing.
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
    
    print(f"Starting Mini App on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Mini App URL: {os.getenv('MINIAPP_URL', 'https://your-domain.com/miniapp')}")
    
    app.run(host=host, port=port, debug=debug)