from fastapi import HTTPException, status, Header, Cookie
import firebase_admin
from firebase_admin import auth, credentials
import os
from app.core.config import settings
from typing import Optional

# Initialize Firebase Admin SDK
if not firebase_admin._apps and settings.firebase_project_id:
    try:
        # Create credentials from environment variables
        firebase_config = {
            "type": "service_account",
            "project_id": settings.firebase_project_id,
            "private_key_id": settings.firebase_private_key_id,
            "private_key": settings.firebase_private_key.replace('\\n', '\n') if settings.firebase_private_key else "",
            "client_email": settings.firebase_client_email,
            "client_id": settings.firebase_client_id,
            "auth_uri": settings.firebase_auth_uri,
            "token_uri": settings.firebase_token_uri,
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": settings.firebase_client_cert_url
        }
        
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
        firebase_initialized = True
        print("✅ Firebase Admin SDK initialized successfully with environment credentials")
    except Exception as e:
        print(f"❌ Firebase Admin SDK initialization failed: {e}")
        raise Exception(f"Failed to initialize Firebase: {e}")
elif not settings.firebase_project_id:
    print("⚠️ Firebase configuration not found. Firebase authentication will be disabled.")

async def verify_firebase_token(authorization: str = Header(None)):
    """Verify Firebase ID token and return the decoded token.
    
    Args:
        authorization: Authorization header containing the Firebase ID token
        
    Returns:
        dict: Decoded Firebase token
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    try:
        print(f"🔐 Authorization header received: {authorization}")
        
        # Check if authorization header is present
        if not authorization:
            print("❌ No authorization header provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header is required"
            )
        
        # Remove "Bearer " prefix if present
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization
            
        print(f"🎫 Token extracted (length: {len(token)}): {token[:50]}...")
        
        # Verify Firebase ID token
        decoded_token = auth.verify_id_token(token)
        print(f"✅ Firebase token decoded successfully: {decoded_token}")
        
        return decoded_token
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"❌ Firebase Auth Error: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase token: {str(e)}"
        )

async def verify_session_cookie(session_cookie: Optional[str] = Cookie(None, alias="auth_session")):
    """Verify Firebase session cookie and return the decoded claims.
    
    Args:
        session_cookie: Session cookie containing the Firebase session token
        
    Returns:
        dict: Decoded Firebase claims
        
    Raises:
        HTTPException: If session cookie is invalid or missing
    """
    try:
        print(f"🍪 Session cookie received: {session_cookie}")
        
        # Check if session cookie is present
        if not session_cookie:
            print("❌ No session cookie provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session cookie is required"
            )
        
        # Verify Firebase session cookie
        decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
        print(f"✅ Firebase session cookie decoded successfully: {decoded_claims}")
        
        return decoded_claims
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"❌ Firebase Session Error: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid session cookie: {str(e)}"
        )

async def get_current_user_id(
    authorization: str = Header(None),
    session_cookie: Optional[str] = Cookie(None, alias="auth_session")
):
    """Extract user ID from verified Firebase token or session cookie.
    
    Args:
        authorization: Authorization header containing the Firebase ID token
        session_cookie: Session cookie containing the Firebase session token
        
    Returns:
        str: User ID from the Firebase token or session cookie
        
    Raises:
        HTTPException: If neither token nor session cookie is valid or missing
    """
    # Try to get user ID from authorization header (Bearer token)
    if authorization:
        try:
            decoded_token = await verify_firebase_token(authorization)
            user_id = decoded_token.get("uid")
            print(f"👤 User ID extracted from token: {user_id}")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: No user ID in payload"
                )
            return user_id
        except HTTPException:
            # If token verification fails, try session cookie
            pass
    
    # Try to get user ID from session cookie
    if session_cookie:
        try:
            decoded_claims = await verify_session_cookie(session_cookie)
            user_id = decoded_claims.get("uid")
            print(f"👤 User ID extracted from session: {user_id}")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid session: No user ID in payload"
                )
            return user_id
        except HTTPException:
            # Both methods failed
            pass
    
    # If we reach here, both methods failed
    print("❌ No valid authentication method provided")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Valid authentication token or session cookie is required"
    )