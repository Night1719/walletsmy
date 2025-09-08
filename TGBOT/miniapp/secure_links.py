"""
Secure dynamic link generation system for instruction files.
Creates temporary access links that expire after 40 minutes.
"""
import secrets
import hashlib
import hmac
import time
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class SecureLinkManager:
    """Manages secure temporary links for instruction files"""
    
    def __init__(self, secret_key: str, link_expiry_minutes: int = 40):
        self.secret_key = secret_key.encode()
        self.link_expiry_minutes = link_expiry_minutes
        self.active_links: Dict[str, Dict] = {}
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def generate_secure_token(self, instruction_type: str, file_format: str, user_id: int) -> str:
        """Generate a secure token for accessing instruction files"""
        # Create payload
        payload = {
            'instruction_type': instruction_type,
            'file_format': file_format,
            'user_id': user_id,
            'timestamp': int(time.time()),
            'nonce': secrets.token_hex(16)
        }
        
        # Encode payload
        payload_json = json.dumps(payload, sort_keys=True)
        payload_b64 = base64.b64encode(payload_json.encode()).decode()
        
        # Create signature
        signature = hmac.new(
            self.secret_key,
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Combine payload and signature
        token = f"{payload_b64}.{signature}"
        
        # Generate additional random string for longer URL
        random_suffix = secrets.token_urlsafe(32)
        
        return f"{token}.{random_suffix}"
    
    def validate_token(self, token: str) -> Optional[Dict]:
        """Validate token and return payload if valid"""
        try:
            # Clean up expired links periodically
            self._cleanup_expired_links()
            
            # Split token
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            payload_b64, signature, random_suffix = parts
            
            # Verify signature
            expected_signature = hmac.new(
                self.secret_key,
                payload_b64.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning(f"Invalid signature for token: {token[:20]}...")
                return None
            
            # Decode payload
            payload_json = base64.b64decode(payload_b64).decode()
            payload = json.loads(payload_json)
            
            # Check if token is in active links (additional security)
            if token in self.active_links:
                link_data = self.active_links[token]
                if link_data['expires_at'] > time.time():
                    return payload
                else:
                    # Remove expired link
                    del self.active_links[token]
                    return None
            
            # Check timestamp (fallback for tokens not in active links)
            token_age = time.time() - payload['timestamp']
            if token_age > (self.link_expiry_minutes * 60):
                logger.warning(f"Token expired: {token_age:.1f}s old")
                return None
            
            return payload
            
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return None
    
    def create_secure_link(self, instruction_type: str, file_format: str, user_id: int, base_url: str) -> str:
        """Create a secure temporary link for instruction file"""
        token = self.generate_secure_token(instruction_type, file_format, user_id)
        
        # Store link data
        expires_at = time.time() + (self.link_expiry_minutes * 60)
        self.active_links[token] = {
            'instruction_type': instruction_type,
            'file_format': file_format,
            'user_id': user_id,
            'created_at': time.time(),
            'expires_at': expires_at,
            'access_count': 0
        }
        
        # Create full URL
        secure_url = f"{base_url.rstrip('/')}/secure/{token}"
        
        logger.info(f"Created secure link for {instruction_type}/{file_format} for user {user_id}")
        return secure_url
    
    def record_access(self, token: str) -> bool:
        """Record access to secure link"""
        if token in self.active_links:
            self.active_links[token]['access_count'] += 1
            return True
        return False
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a specific token"""
        if token in self.active_links:
            del self.active_links[token]
            logger.info(f"Revoked token: {token[:20]}...")
            return True
        return False
    
    def _cleanup_expired_links(self):
        """Remove expired links from memory"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        expired_tokens = []
        for token, data in self.active_links.items():
            if data['expires_at'] <= current_time:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del self.active_links[token]
        
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired links")
        
        self.last_cleanup = current_time
    
    def get_link_stats(self) -> Dict:
        """Get statistics about active links"""
        current_time = time.time()
        active_count = 0
        total_accesses = 0
        
        for data in self.active_links.values():
            if data['expires_at'] > current_time:
                active_count += 1
                total_accesses += data['access_count']
        
        return {
            'active_links': active_count,
            'total_accesses': total_accesses,
            'expired_links': len(self.active_links) - active_count
        }

# Global instance
link_manager = None

def init_link_manager(secret_key: str, link_expiry_minutes: int = 40):
    """Initialize the global link manager"""
    global link_manager
    link_manager = SecureLinkManager(secret_key, link_expiry_minutes)
    logger.info(f"Link manager initialized with {link_expiry_minutes} minute expiry")

def get_link_manager() -> SecureLinkManager:
    """Get the global link manager instance"""
    if link_manager is None:
        raise RuntimeError("Link manager not initialized")
    return link_manager