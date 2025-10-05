import jwt
import httpx
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import SERVICES
import asyncio
import time

logger = logging.getLogger(__name__)

# Cache for JWKS keys
jwks_cache: Optional[Dict[str, Any]] = None
jwks_cache_time: float = 0
JWKS_CACHE_DURATION = 3600  # 1 hour

class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.auth_service_url = SERVICES["auth"]["url"]

    async def dispatch(self, request: Request, call_next):
        logger.info(f"JWT Middleware processing: {request.method} {request.url.path}")
        logger.info(f"Full URL: {request.url}")
        logger.info(f"Authorization header present: {'Authorization' in request.headers}")
        
        # Skip authentication for health check, JWKS endpoints, and OPTIONS requests
        if request.url.path in ["/health", "/.well-known/jwks.json"] or request.method == "OPTIONS":
            logger.info(f"Skipping JWT check for: {request.url.path}")
            return await call_next(request)
            
        # Define publicly accessible endpoints (no authentication required) - only GET requests
        public_endpoints = [
            "/api/products",
            "/api/categories"
        ]
        
        # Check if this is a publicly accessible endpoint (only for GET requests)
        is_public = (request.method == "GET" and 
                    any(request.url.path.startswith(endpoint) for endpoint in public_endpoints))
        
        # Check if this is a protected path (requires authentication)
        # Only cart and wishlist endpoints require authentication
        protected_paths = ["/api/v1/cart", "/api/v1/wishlist"]
        is_protected = any(request.url.path.startswith(path) for path in protected_paths)
        
        logger.info(f"Path analysis: is_public={is_public}, is_protected={is_protected}, method={request.method}")
        
        # Extract token from either Authorization header or session cookie
        token = None
        auth_header = request.headers.get("Authorization")
        
        # First, try Authorization header
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            logger.info(f"Token found in Authorization header for path: {request.url.path}")
        else:
            # Try to get token from session cookie
            cookies = request.cookies
            session_token = cookies.get("auth_session")
            if session_token:
                token = session_token
                logger.info(f"Session token found in cookie for path: {request.url.path}")
                logger.info(f"Session token preview: {token[:50]}...")
            else:
                logger.info(f"No token found in Authorization header or session cookie")
        
        # Store token for forwarding to downstream services
        if token:
            request.state.token = token
            request.state.auth_source = "header" if auth_header else "session"
            logger.info(f"Token stored for forwarding, source: {request.state.auth_source}")
        
        # Authentication check - only for truly protected paths (cart/wishlist)
        if is_protected:
            if not token:
                logger.warning(f"Missing authentication for protected path: {request.url.path}")
                logger.warning(f"Headers received: {dict(request.headers)}")
                logger.warning(f"Cookies received: {dict(request.cookies)}")
                raise HTTPException(status_code=401, detail="Authentication required")
            else:
                logger.info(f"Authentication present for protected path: {request.url.path}")
        else:
            logger.info(f"Path {request.url.path} is not protected, proceeding without auth check")
        
        # Continue with the request
        response = await call_next(request)
        return response

    async def get_public_key(self) -> Optional[Dict[str, Any]]:
        """Fetch public key from Auth Service JWKS endpoint with caching"""
        global jwks_cache, jwks_cache_time
        
        current_time = time.time()
        
        # Return cached key if still valid
        if jwks_cache and (current_time - jwks_cache_time) < JWKS_CACHE_DURATION:
            return jwks_cache
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.auth_service_url}/.well-known/jwks.json")
                if response.status_code == 200:
                    jwks_data = response.json()
                    
                    # Extract public key from JWKS (simplified - in real implementation, 
                    # you would need to properly parse the JWKS format)
                    if "keys" in jwks_data and len(jwks_data["keys"]) > 0:
                        # For now, we'll cache the raw JWKS data
                        # In a real implementation, you would convert this to a usable public key
                        jwks_cache = jwks_data
                        jwks_cache_time = current_time
                        return jwks_data
                    
            return None
        except Exception as e:
            logger.error(f"Error fetching JWKS: {str(e)}")
            return None