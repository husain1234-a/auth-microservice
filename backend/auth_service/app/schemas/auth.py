from pydantic import BaseModel, validator
import phonenumbers

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

class UserResponse(BaseModel):
    uid: str
    email: str | None
    phone_number: str | None
    display_name: str | None
    photo_url: str | None

class AuthResponse(BaseModel):
    user: UserResponse
    message: str