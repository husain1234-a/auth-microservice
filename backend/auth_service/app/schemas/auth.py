from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional
import phonenumbers
from ..models.user import UserRole

class GoogleLoginRequest(BaseModel):
    id_token: str

class PhoneOTPRequest(BaseModel):
    phone_number: str
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        try:
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError('Invalid phone number')
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError('Invalid phone number format')

class VerifyOTPRequest(BaseModel):
    phone_number: str
    otp: str
    challenge_id: str

class UpdateRoleRequest(BaseModel):
    uid: str
    role: UserRole

class UserResponse(BaseModel):
    uid: str
    email: Optional[str]
    phone_number: Optional[str]
    display_name: Optional[str]
    photo_url: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    user: UserResponse
    message: str