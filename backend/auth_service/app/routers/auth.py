from fastapi import APIRouter, HTTPException, Request, Response, Depends, Cookie
from ..schemas.auth import GoogleLoginRequest, PhoneOTPRequest, AuthResponse, UserResponse
from ..services.auth_service import AuthService
from config.settings import settings
from typing import Optional

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/google-login", response_model=AuthResponse)
async def google_login(request: GoogleLoginRequest, response: Response):
    # Verify ID token
    decoded_token = await AuthService.verify_id_token(request.id_token)
    
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
    
    user = AuthService.format_user_response(decoded_token)
    return AuthResponse(user=user, message="Login successful")

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
async def get_current_user(session_cookie: Optional[str] = Cookie(None, alias=settings.session_cookie_name)):
    if not session_cookie:
        raise HTTPException(status_code=401, detail="No session found")
    
    decoded_claims = await AuthService.verify_session_cookie(session_cookie)
    return AuthService.format_user_response(decoded_claims)

@router.post("/update-phone", response_model=dict)
async def update_phone_number(request: PhoneOTPRequest, session_cookie: Optional[str] = Cookie(None, alias=settings.session_cookie_name)):
    if not session_cookie:
        raise HTTPException(status_code=401, detail="No session found")
    
    # Verify current session
    decoded_claims = await AuthService.verify_session_cookie(session_cookie)
    
    # Store the phone number (in a real implementation, you would save this to your database)
    # For now, we'll just return success since we're only collecting the phone number
    
    return {"message": "Phone number saved successfully", "phone_number": request.phone_number}

@router.post("/logout")
async def logout(response: Response, session_cookie: Optional[str] = Cookie(None, alias=settings.session_cookie_name)):
    if session_cookie:
        try:
            decoded_claims = await AuthService.verify_session_cookie(session_cookie)
            await AuthService.revoke_refresh_tokens(decoded_claims['uid'])
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