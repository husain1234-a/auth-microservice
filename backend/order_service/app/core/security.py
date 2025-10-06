import httpx
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends, Request
from jose import JWTError, jwt
from app.core.config import settings
import json
import base64

logger = logging.getLogger(__name__)

# Cache for JWKS keys
jwks_cache: Optional[Dict[str, Any]] = None
jwks_cache_time: float = 0
JWKS_CACHE_DURATION = 3600  # 1 hour

# Firebase public keys cache
firebase_keys_cache: Optional[Dict[str, Any]] = None
firebase_keys_cache_time: float = 0

async def get_public_key() -> Optional[Dict[str, Any]]:
    """Fetch public key from Auth Service JWKS endpoint with caching"""
    global jwks_cache, jwks_cache_time
    import time
    current_time = time.time()
    
    # Return cached key if still valid
    if jwks_cache and (current_time - jwks_cache_time) < JWKS_CACHE_DURATION:
        return jwks_cache
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.user_service_url}/.well-known/jwks.json")
            if response.status_code == 200:
                jwks_data = response.json()
                jwks_cache = jwks_data
                jwks_cache_time = current_time
                return jwks_data
        
        return None
    except Exception as e:
        logger.error(f"Error fetching JWKS: {str(e)}")
        return None

async def get_firebase_public_keys() -> Optional[Dict[str, Any]]:
    """Fetch Firebase public keys for session cookie verification"""
    global firebase_keys_cache, firebase_keys_cache_time
    import time
    current_time = time.time()
    
    # Return cached keys if still valid
    if firebase_keys_cache and (current_time - firebase_keys_cache_time) < JWKS_CACHE_DURATION:
        return firebase_keys_cache
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com")
            if response.status_code == 200:
                keys_data = response.json()
                firebase_keys_cache = keys_data
                firebase_keys_cache_time = current_time
                return keys_data
        
        return None
    except Exception as e:
        logger.error(f"Error fetching Firebase public keys: {str(e)}")
        return None

def is_firebase_session_token(token: str) -> bool:
    """Check if token is a Firebase session token by examining its structure"""
    try:
        # Decode the header without verification to check issuer
        header = jwt.get_unverified_header(token)
        payload = jwt.get_unverified_claims(token)
        
        # Firebase session tokens have specific issuer pattern
        issuer = payload.get("iss", "")
        return "session.firebase.google.com" in issuer
    except:
        return False

async def verify_firebase_session_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify Firebase session token"""
    try:
        # For now, we'll do basic validation without full cryptographic verification
        # In production, you would want to verify the signature using Firebase's public keys
        payload = jwt.get_unverified_claims(token)
        
        # Basic validation
        issuer = payload.get("iss", "")
        if "session.firebase.google.com" not in issuer:
            logger.error(f"Invalid issuer: {issuer}")
            return None
        
        # Check expiration
        import time
        exp = payload.get("exp", 0)
        if exp < time.time():
            logger.error("Token expired")
            return None
        
        # Check audience (should match your Firebase project ID)
        aud = payload.get("aud", "")
        if not aud:
            logger.error("Missing audience")
            return None
        
        logger.info(f"Firebase session token verified for user: {payload.get('user_id', 'unknown')}")
        return payload
        
    except Exception as e:
        logger.error(f"Error verifying Firebase session token: {str(e)}")
        return None

async def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token - handles both local and Firebase session tokens"""
    try:
        # Check if this is a Firebase session token
        if is_firebase_session_token(token):
            logger.info("Detected Firebase session token, using Firebase verification")
            return await verify_firebase_session_token(token)
        
        # Handle local JWT tokens
        logger.info("Detected local JWT token, using local verification")
        
        # Get public key from JWKS
        jwks = await get_public_key()
        if not jwks or "keys" not in jwks or len(jwks["keys"]) == 0:
            logger.error("No valid JWKS found")
            return None
        
        # For now, we'll use a simplified approach
        # In a real implementation, you would properly parse the JWKS and use the correct key
        # based on the token's kid header
        
        # Decode the token (this is a simplified implementation)
        # In a real scenario, you would use the actual public key from JWKS
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as e:
        logger.error(f"JWT verification error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        return None

async def get_current_user(request: Request) -> Dict[str, Any]:
    """Get current user from request headers with dual-mode support"""
    # Check for X-Auth-Source header to determine authentication mode
    auth_source = request.headers.get("X-Auth-Source")
    
    # Check for Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header"
        )
    
    token = auth_header.split(" ")[1]
    
    if auth_source == "gateway":
        # Gateway mode: Token was already validated at the gateway
        # We still need to verify it locally for zero-trust security
        payload = await verify_jwt_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        return payload
    else:
        # Legacy mode: Direct call to service, validate token locally
        payload = await verify_jwt_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        return payload

async def get_current_admin_user(request: Request) -> Dict[str, Any]:
    """Get current admin user from request headers with dual-mode support"""
    user = await get_current_user(request)
    
    # Check if user has admin role
    role = user.get("role")
    if role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user

async def get_current_user_id(request: Request) -> str:
    """Extract user ID from verified JWT token with dual-mode support"""
    user = await get_current_user(request)
    # Try both 'uid' (Firebase) and 'user_id' (Firebase session) fields
    user_id = user.get("uid") or user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: No user ID in payload"
        )
    
    return str(user_id)

async def get_current_delivery_partner(request: Request) -> Dict[str, Any]:
    """Get current delivery partner from request headers with dual-mode support"""
    user = await get_current_user(request)
    
    # Check if user has delivery partner role
    role = user.get("role")
    if role != "delivery_partner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Delivery partner access required"
        )
    
    return user

# Dependency functions for FastAPI
async def get_current_user_dependency(request: Request) -> Dict[str, Any]:
    return await get_current_user(request)

async def get_current_admin_user_dependency(request: Request) -> Dict[str, Any]:
    return await get_current_admin_user(request)

async def get_current_delivery_partner_dependency(request: Request) -> Dict[str, Any]:
    return await get_current_delivery_partner(request)

async def get_current_user_id_dependency(request: Request) -> str:
    return await get_current_user_id(request)