from fastapi import HTTPException, status, Header
from jose import JWTError, jwt
from app.core.config import settings

async def get_current_user_id(authorization: str = Header(...)):
    try:
        print(f"Authorization header received: {authorization}")
        # Remove "Bearer " prefix if present
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization
            
        print(f"Token extracted: {token}")
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        print(f"Payload decoded: {payload}")
        user_id = payload.get("sub")
        print(f"User ID extracted: {user_id}")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: No user ID in payload"
            )
        return user_id  # Return as string to match the users table
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )