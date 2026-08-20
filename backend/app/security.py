"""Security utilities - Authentication and Rate Limiting"""
import os
import time
from typing import Optional
from collections import defaultdict
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta

# Simple API key authentication (replace with JWT for production)
VALID_API_KEYS = set(os.getenv("API_KEYS", "").split(","))
API_KEY_ENABLED = os.getenv("ENABLE_AUTH", "false").lower() == "true"

security = HTTPBearer(auto_error=False)

async def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Verify API key authentication"""
    if not API_KEY_ENABLED:
        return True  # Auth disabled in development
    
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication credentials"
        )
    
    if credentials.credentials not in VALID_API_KEYS:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    
    return True

# Rate limiting (in-memory, use Redis for production)
class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
        self.window = 60  # seconds
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.requests_per_minute:
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True
    
    def cleanup(self):
        """Cleanup old entries"""
        now = time.time()
        for client_id in list(self.requests.keys()):
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if now - req_time < self.window
            ]
            if not self.requests[client_id]:
                del self.requests[client_id]

# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60)

async def check_rate_limit(request: Request):
    """Check rate limit for request"""
    client_ip = request.client.host
    
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    return True

# File size validation
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB default

async def validate_file_size(file_content: bytes):
    """Validate uploaded file size"""
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.0f}MB"
        )
    return True

# Input sanitization
def sanitize_input(text: str, max_length: int = 5000) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Trim to max length
    text = text[:max_length]
    
    # Remove potential injection attempts
    text = text.replace("<script>", "").replace("</script>", "")
    text = text.replace("javascript:", "")
    
    return text.strip()
