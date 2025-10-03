import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.core.config import settings

class AuthClient:
    """Client for communicating with the Auth Service"""
    
    @staticmethod
    async def verify_session(session_cookie: str) -> Optional[Dict[str, Any]]:
        """
        Verify session cookie with auth service
        Returns user data if valid, None if invalid
        """
        if not session_cookie:
            return None
            
        async with httpx.AsyncClient() as client:
            try:
                # Make request to auth service to verify session
                response = await client.get(
                    f"{settings.user_service_url}/auth/me",
                    cookies={"auth_session": session_cookie}
                )
                
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception:
                return None
    
    @staticmethod
    async def verify_user(session_cookie: str) -> str:
        """
        Verify that the session is valid and return the user ID
        Raises HTTPException if invalid
        """
        if not session_cookie:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session cookie is required"
            )
            
        user_data = await AuthClient.verify_session(session_cookie)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session cookie"
            )
            
        user_id = user_data.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session: No user ID in payload"
            )
            
        return user_id
    
    @staticmethod
    async def verify_admin(session_cookie: str) -> bool:
        """
        Verify that the user is an admin
        Returns True if user is admin, False otherwise
        """
        user_data = await AuthClient.verify_session(session_cookie)
        if not user_data:
            return False
            
        # Check if user has admin role
        role = user_data.get("role")
        return role in ["admin", "owner"]