from firebase_admin import auth
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.auth import UserResponse
from ..models.user import User, UserRole
from .user_service import UserService
import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime

class AuthService:
    # Cache for JWKS
    _jwks_cache: Optional[Dict[str, Any]] = None
    _jwks_cache_time: float = 0
    _jwks_cache_duration: int = 3600  # 1 hour
    _project_id: Optional[str] = None
    
    @staticmethod
    async def verify_id_token(id_token: str) -> dict:
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    @staticmethod
    async def create_session_cookie(id_token: str, expires_in: int = 3600 * 24 * 5) -> str:
        try:
            session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)
            return session_cookie
        except Exception as e:
            raise HTTPException(status_code=401, detail="Failed to create session")
    
    @staticmethod
    async def verify_session_cookie(session_cookie: str) -> dict:
        try:
            decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
            return decoded_claims
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid session")
    
    @staticmethod
    async def revoke_refresh_tokens(uid: str):
        try:
            auth.revoke_refresh_tokens(uid)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to revoke tokens")
    
    @staticmethod
    async def get_or_create_user_from_token(db: AsyncSession, decoded_token: dict) -> User:
        """Get or create user from Firebase token data"""
        uid = decoded_token.get('uid')
        email = decoded_token.get('email')
        phone_number = decoded_token.get('phone_number')
        display_name = decoded_token.get('name')
        photo_url = decoded_token.get('picture')
        
        # Handle potential None values
        if uid is None:
            raise HTTPException(status_code=400, detail="UID is required")
        
        user, created = await UserService.get_or_create_user(
            db=db,
            uid=str(uid),
            email=str(email) if email is not None else None,
            phone_number=str(phone_number) if phone_number is not None else None,
            display_name=str(display_name) if display_name is not None else None,
            photo_url=str(photo_url) if photo_url is not None else None,
            role=UserRole.CUSTOMER  # Default role for new users
        )
        
        return user
    
    @staticmethod
    def format_user_response(user: User) -> UserResponse:
        return UserResponse(
            uid=str(user.uid),
            email=str(user.email) if user.email is not None else None,
            phone_number=str(user.phone_number) if user.phone_number is not None else None,
            display_name=str(user.display_name) if user.display_name is not None else None,
            photo_url=str(user.photo_url) if user.photo_url is not None else None,
            role=UserRole(user.role),  # Convert to enum
            is_active=bool(user.is_active),
            created_at=user.created_at if isinstance(user.created_at, datetime) else datetime.now(),
            updated_at=user.updated_at if isinstance(user.updated_at, datetime) else datetime.now()
        )
    
    @classmethod
    async def get_jwks(cls) -> Dict[str, Any]:
        """Fetch Firebase JWKS for token validation"""
        import time
        current_time = time.time()
        
        # Return cached JWKS if still valid
        if cls._jwks_cache and (current_time - cls._jwks_cache_time) < cls._jwks_cache_duration:
            return cls._jwks_cache
        
        try:
            # Get Firebase project ID
            if not cls._project_id:
                # In a real implementation, you would get this from Firebase config
                # For now, we'll use a placeholder
                cls._project_id = "your-firebase-project-id"
            
            # Fetch JWKS from Firebase
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
                )
                
                if response.status_code == 200:
                    keys_data = response.json()
                    
                    # Convert to JWKS format
                    keys = []
                    for kid, public_key in keys_data.items():
                        # This is a simplified conversion
                        # In a real implementation, you would properly parse the public key
                        keys.append({
                            "alg": "RS256",
                            "e": "AQAB",  # Standard exponent
                            "kid": kid,
                            "kty": "RSA",
                            "n": "modulus-placeholder",  # Would extract from public_key
                            "use": "sig"
                        })
                    
                    jwks = {"keys": keys}
                    cls._jwks_cache = jwks
                    cls._jwks_cache_time = current_time
                    return jwks
                
            return {"keys": []}
        except Exception as e:
            # Return empty JWKS on error
            return {"keys": []}