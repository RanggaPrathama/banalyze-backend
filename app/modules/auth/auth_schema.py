from pydantic import BaseModel, EmailStr

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None
    type: str = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    id: str
    nama_user: str
    email: EmailStr
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
class RegisterRequest(BaseModel):
    nama_user: str
    email: EmailStr
    password: str

class RegisterResponse(BaseModel):
    id: str
    nama_user: str
    email: EmailStr
    access_token: str
    refresh_token: str
token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str
