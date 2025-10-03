from fastapi import HTTPException, status, Header, Cookie
from app.core.config import settings
from app.core.auth_client import AuthClient
from typing import Optional

async def verify_firebase_token(authorization: str = Header(None)):
    """Verify Firebase ID token by calling the Auth Service.
    
    Args:
        authorization: Authorization header containing the Firebase ID token
        
    Returns:
        dict: Decoded token data
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    # For now, we'll raise an error since we're using session cookies
    # In a real implementation, you might want to verify with the Auth Service
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="This service uses session cookies for authentication, not Firebase tokens"
    )

async def verify_session_cookie(session_cookie: Optional[str] = Cookie(None, alias="auth_session")):
    """Verify session cookie by calling the Auth Service.
    
    Args:
        session_cookie: Session cookie to verify
        
    Returns:
        dict: User data if valid
        
    Raises:
        HTTPException: If session cookie is invalid or missing
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
    
    return user_data

async def get_current_user_id(
    authorization: str = Header(None),
    session_cookie: Optional[str] = Cookie(None, alias="auth_session")
):
    """Extract user ID from verified session cookie by calling the Auth Service.
    
    Args:
        authorization: Authorization header (not used in this implementation)
        session_cookie: Session cookie to verify
        
    Returns:
        str: User ID
        
    Raises:
        HTTPException: If session cookie is invalid or missing
    """
    # We only support session cookies, not authorization headers
    if authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This service uses session cookies for authentication, not Firebase tokens"
        )
    
    # Get user ID from session cookie
    if session_cookie:
        return await AuthClient.verify_user(session_cookie)
    
    # If we reach here, no valid authentication method was provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Valid session cookie is required"
    )