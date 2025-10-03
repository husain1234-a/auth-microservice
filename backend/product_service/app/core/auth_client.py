import httpx
from typing import Optional, Dict, Any
from app.core.config import settings

class AuthClient:
    """Client for communicating with the Auth Service"""
    
    @staticmethod
    async def verify_session(session_cookie: Optional[str]) -> Optional[Dict[str, Any]]:
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
                    f"{settings.auth_service_url}/auth/me",
                    cookies={"auth_session": session_cookie}
                )
                
                if response.status_code == 200:
                    return response.json()
                return None
            except Exception:
                return None
    
    @staticmethod
    async def verify_admin(session_cookie: Optional[str]) -> bool:
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