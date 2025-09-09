"""
Secure link management for Mini App
Creates temporary, secure links for instruction files
"""
import hmac
import hashlib
import time
import json
import base64
from typing import Optional, Dict, Any

class SecureLinkManager:
    def __init__(self, secret_key: str, link_expiry_minutes: int = 40):
        self.secret_key = secret_key.encode()
        self.link_expiry_minutes = link_expiry_minutes
        self.access_log = {}  # Track access attempts
    
    def create_secure_link(self, instruction_type: str, file_format: str, user_id: int, base_url: str) -> str:
        """Create a secure temporary link"""
        # Create payload
        payload = {
            "instruction_type": instruction_type,
            "file_format": file_format,
            "user_id": user_id,
            "timestamp": int(time.time()),
            "expires_at": int(time.time()) + (self.link_expiry_minutes * 60)
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
        
        # Create token
        token = f"{payload_b64}.{signature}"
        
        # Create secure URL
        secure_url = f"{base_url}/secure/{token}"
        
        return secure_url
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate a secure token and return payload if valid"""
        try:
            # Split token
            if '.' not in token:
                return None
            
            payload_b64, signature = token.split('.', 1)
            
            # Verify signature
            expected_signature = hmac.new(
                self.secret_key,
                payload_b64.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return None
            
            # Decode payload
            payload_json = base64.b64decode(payload_b64).decode()
            payload = json.loads(payload_json)
            
            # Check expiration
            current_time = int(time.time())
            if current_time > payload.get('expires_at', 0):
                return None
            
            return payload
            
        except Exception:
            return None
    
    def record_access(self, token: str):
        """Record access attempt for monitoring"""
        current_time = int(time.time())
        if token not in self.access_log:
            self.access_log[token] = []
        
        self.access_log[token].append(current_time)
        
        # Clean old access logs (older than 1 hour)
        cutoff_time = current_time - 3600
        self.access_log[token] = [
            access_time for access_time in self.access_log[token]
            if access_time > cutoff_time
        ]
    
    def get_access_stats(self, token: str) -> Dict[str, Any]:
        """Get access statistics for a token"""
        if token not in self.access_log:
            return {"access_count": 0, "last_access": None}
        
        access_times = self.access_log[token]
        return {
            "access_count": len(access_times),
            "last_access": max(access_times) if access_times else None,
            "access_times": access_times
        }

# Global link manager instance
_link_manager = None

def init_link_manager(secret_key: str, link_expiry_minutes: int = 40):
    """Initialize the global link manager"""
    global _link_manager
    _link_manager = SecureLinkManager(secret_key, link_expiry_minutes)

def get_link_manager() -> SecureLinkManager:
    """Get the global link manager instance"""
    if _link_manager is None:
        raise RuntimeError("Link manager not initialized. Call init_link_manager() first.")
    return _link_manager