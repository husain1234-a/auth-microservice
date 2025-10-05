from fastapi import APIRouter, HTTPException, Request, Response, Depends, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.auth import GoogleLoginRequest, PhoneOTPRequest, AuthResponse, UserResponse, UpdateRoleRequest
from ..services.auth_service import AuthService
from ..services.user_service import UserService
from ..database import get_db
from ..models.user import UserRole
from config.settings import settings
from typing import Optional
import json

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/google-login", response_model=AuthResponse)
async def google_login(request: GoogleLoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    # Verify ID token
    decoded_token = await AuthService.verify_id_token(request.id_token)
    
    # Get or create user in database
    user = await AuthService.get_or_create_user_from_token(db, decoded_token)
    
    # Create session cookie
    session_cookie = await AuthService.create_session_cookie(request.id_token)
    
    # Set HTTP-only cookie
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_cookie,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=3600 * 24 * 5  # 5 days
    )
    
    user_response = AuthService.format_user_response(user)
    return AuthResponse(user=user_response, message="Login successful")

# @router.post("/send-otp")
# async def send_otp(request: PhoneOTPRequest, req: Request):
#     client_ip = req.client.host
    
#     # Rate limiting
#     await rate_limiter.check_otp_rate_limit(request.phone_number, client_ip)
    
#     # This endpoint validates phone number and enforces rate limiting
#     # The actual OTP sending is handled by Firebase client SDK
#     return {"message": "Phone number validated. Proceed with OTP verification."}

# @router.post("/verify-otp", response_model=AuthResponse)
# async def verify_otp(request: VerifyOTPRequest, response: Response):
#     # In a real implementation, you would verify the OTP with Firebase
#     # For now, we assume the frontend has already verified with Firebase
#     # and provides a valid ID token through the challenge_id
    
#     try:
#         # Verify the challenge (this would contain the Firebase ID token)
#         decoded_token = await AuthService.verify_id_token(request.challenge_id)
        
#         # Ensure phone number matches
#         if decoded_token.get('phone_number') != request.phone_number:
#             raise HTTPException(status_code=400, detail="Phone number mismatch")
        
#         # Create session cookie
#         session_cookie = await AuthService.create_session_cookie(request.challenge_id)
        
#         # Set HTTP-only cookie
#         response.set_cookie(
#             key=settings.session_cookie_name,
#             value=session_cookie,
#             httponly=True,
#             secure=settings.is_production,
#             samesite="lax",
#             max_age=3600 * 24 * 5
#         )
        
#         user = AuthService.format_user_response(decoded_token)
#         return AuthResponse(user=user, message="Phone verification successful")
        
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Invalid OTP or challenge")

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    session_cookie: Optional[str] = Cookie(None, alias=settings.session_cookie_name)
):
    if not session_cookie:
        raise HTTPException(status_code=401, detail="No session found")
    
    decoded_claims = await AuthService.verify_session_cookie(session_cookie)
    uid = decoded_claims.get('uid')
    
    # Check if uid is present
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid session token")
    
    user = await UserService.get_user_by_uid(db, str(uid))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return AuthService.format_user_response(user)

@router.post("/update-phone", response_model=UserResponse)
async def update_phone_number(
    request: PhoneOTPRequest, 
    db: AsyncSession = Depends(get_db),
    session_cookie: Optional[str] = Cookie(None, alias=settings.session_cookie_name)
):
    if not session_cookie:
        raise HTTPException(status_code=401, detail="No session found")
    
    # Verify current session
    decoded_claims = await AuthService.verify_session_cookie(session_cookie)
    uid = decoded_claims.get('uid')
    
    # Check if uid is present
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid session token")
    
    # Update phone number in database
    user = await UserService.update_user_phone(db, str(uid), request.phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return AuthService.format_user_response(user)

@router.post("/logout")
async def logout(response: Response, session_cookie: Optional[str] = Cookie(None, alias=settings.session_cookie_name)):
    if session_cookie:
        try:
            decoded_claims = await AuthService.verify_session_cookie(session_cookie)
            uid = decoded_claims.get('uid')
            if uid:
                await AuthService.revoke_refresh_tokens(str(uid))
        except:
            pass  # Continue with logout even if session is invalid
    
    # Clear cookie
    response.delete_cookie(
        key=settings.session_cookie_name,
        httponly=True,
        secure=settings.is_production,
        samesite="lax"
    )
    
    return {"message": "Logout successful"}

@router.post("/update-role", response_model=UserResponse)
async def update_user_role(
    request: UpdateRoleRequest,
    db: AsyncSession = Depends(get_db),
    session_cookie: Optional[str] = Cookie(None, alias=settings.session_cookie_name)
):
    if not session_cookie:
        raise HTTPException(status_code=401, detail="No session found")
    
    # Verify current session
    decoded_claims = await AuthService.verify_session_cookie(session_cookie)
    current_user_uid = decoded_claims.get('uid')
    
    # Check if uid is present
    if not current_user_uid:
        raise HTTPException(status_code=401, detail="Invalid session token")
    
    # Get current user to check permissions
    current_user = await UserService.get_user_by_uid(db, str(current_user_uid))
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    # Only admins and owners can update roles
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to update roles")
    
    # Update the target user's role
    user = await UserService.update_user_role(db, request.uid, request.role)
    if not user:
        raise HTTPException(status_code=404, detail="Target user not found")
    
    return AuthService.format_user_response(user)

@router.get("/users/{uid}", response_model=UserResponse)
async def get_user_by_uid(
    uid: str,
    db: AsyncSession = Depends(get_db),
    session_cookie: Optional[str] = Cookie(None, alias=settings.session_cookie_name)
):
    if not session_cookie:
        raise HTTPException(status_code=401, detail="No session found")
    
    # Verify current session
    decoded_claims = await AuthService.verify_session_cookie(session_cookie)
    current_user_uid = decoded_claims.get('uid')
    
    # Check if uid is present
    if not current_user_uid:
        raise HTTPException(status_code=401, detail="Invalid session token")
    
    # Get current user to check permissions
    current_user = await UserService.get_user_by_uid(db, str(current_user_uid))
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    # Users can view their own profile, admins and owners can view any profile
    if current_user_uid != uid and current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to view this user")
    
    user = await UserService.get_user_by_uid(db, uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return AuthService.format_user_response(user)

@router.get("/.well-known/jwks.json")
async def jwks():
    """
    Expose public keys for JWT validation.
    """
    jwks_data = await AuthService.get_jwks()
    return jwks_data