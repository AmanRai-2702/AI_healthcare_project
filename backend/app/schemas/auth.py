from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID




class PatientRegistrationRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AuthUserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)




class RegistrationResponse(BaseModel):
    message: str
    user: AuthUserResponse


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUserResponse