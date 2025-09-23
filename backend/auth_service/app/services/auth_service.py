from firebase_admin import auth
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.auth import UserResponse
from ..models.user import User, UserRole
from .user_service import UserService

class AuthService:
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
        
        user, created = await UserService.get_or_create_user(
            db=db,
            uid=uid,
            email=email,
            phone_number=phone_number,
            display_name=display_name,
            photo_url=photo_url,
            role=UserRole.CUSTOMER  # Default role for new users
        )
        
        return user
    
    @staticmethod
    def format_user_response(user: User) -> UserResponse:
        return UserResponse(
            uid=user.uid,
            email=user.email,
            phone_number=user.phone_number,
            display_name=user.display_name,
            photo_url=user.photo_url,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )