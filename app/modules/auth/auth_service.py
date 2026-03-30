from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import jwt
from jwt.exceptions import PyJWTError
from app.core.config import settings
from app.modules.user.user_service import UserService
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.modules.auth.auth_schema import RegisterRequest, LoginRequest, LoginResponse, RegisterResponse

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)

    async def register_user(self, data: RegisterRequest) -> RegisterResponse:
        existing_user = await self.user_service.get_user_by_email(data.email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
            
        hashed_password = get_password_hash(data.password)
        user_data_dict = data.model_dump()
        user_data_dict["password"] = hashed_password
        
        new_user = await self.user_service.create_user(user_data_dict)

        tokens = self.create_tokens(str(new_user.id))

        user_dict = {
            "id": str(new_user.id),
            "nama_user": new_user.nama_user,
            "email": new_user.email,
            "avatar_url": new_user.avatar_url
        }

        return RegisterResponse(
            **user_dict,
            **tokens
        )

    async def authenticate_user(self, email: str, password: str)-> LoginResponse:
        user = await self.user_service.get_user_by_email(email)
        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        tokens = self.create_tokens(str(user.id))

        user_dict = {
            "id": str(user.id),
            "nama_user": user.nama_user,
            "email": user.email,
            "avatar_url": user.avatar_url
        }

        return LoginResponse(
            **user_dict,
            **tokens
        )

    def create_tokens(self, user_id: str):
        access_token = create_access_token(data={"sub": user_id})
        refresh_token = create_refresh_token(data={"sub": user_id})
        return {
            "access_token": access_token, 
            "refresh_token": refresh_token, 
            "token_type": "bearer"
        }
