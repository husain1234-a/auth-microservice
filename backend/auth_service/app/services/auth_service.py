from firebase_admin import auth
from fastapi import HTTPException
from ..schemas.auth import UserResponse

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
    def format_user_response(user_record: dict) -> UserResponse:
        return UserResponse(
            uid=user_record.get('uid'),
            email=user_record.get('email'),
            phone_number=user_record.get('phone_number'),
            display_name=user_record.get('name'),
            photo_url=user_record.get('picture')
        )