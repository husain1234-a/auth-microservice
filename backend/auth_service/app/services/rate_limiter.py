import redis
from fastapi import HTTPException, Request
from config.settings import settings
import time

class RateLimiter:
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url)
    
    async def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        try:
            current = self.redis_client.get(key)
            if current is None:
                self.redis_client.setex(key, window, 1)
                return True
            
            if int(current) >= limit:
                return False
            
            self.redis_client.incr(key)
            return True
        except Exception:
            return True  # Allow request if Redis is down
    
    async def check_otp_rate_limit(self, phone_number: str, ip_address: str):
        phone_key = f"otp_phone:{phone_number}"
        ip_key = f"otp_ip:{ip_address}"
        
        # 3 attempts per phone per hour
        phone_allowed = await self.check_rate_limit(phone_key, 3, 3600)
        # 10 attempts per IP per hour
        ip_allowed = await self.check_rate_limit(ip_key, 10, 3600)
        
        if not phone_allowed:
            raise HTTPException(status_code=429, detail="Too many OTP requests for this phone number")
        if not ip_allowed:
            raise HTTPException(status_code=429, detail="Too many OTP requests from this IP")

rate_limiter = RateLimiter()