"""
JWT Security utilities for Cart Service

This module provides utilities for handling authentication
with proper JWT validation as per the microservice architecture plan.
"""

from fastapi import Depends, HTTPException, status, Header
import jwt
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def verify_jwt_token(authorization: str = Header(None)) -> dict:
    """Verify JWT token and return decoded payload.
    
    Args:
        authorization: Authorization header value (Bearer <token>)
        
    Returns:
        dict: Decoded JWT payload
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not authorization:
        logger.warning("Authorization header missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required"
        )
    
    try:
        # Extract token (Bearer <token>)
        token_parts = authorization.split(" ")
        if len(token_parts) != 2 or token_parts[0] != "Bearer":
            logger.warning("Invalid Authorization header format")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header format"
            )
        
        token = token_parts[1]
        
        # Decode and validate token
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("uid")
        
        if not user_id:
            logger.warning("User ID missing from token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: No user ID in payload"
            )
        
        logger.info(f"Authenticated user: {user_id}")
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user(authorization: str = Header(None)) -> dict:
    """Dependency to get current user from JWT token.
    
    This should be used as a FastAPI dependency in route handlers.
    
    Args:
        authorization: Authorization header (automatically injected by FastAPI)
        
    Returns:
        dict: User information from JWT payload
    """
    return await verify_jwt_token(authorization)