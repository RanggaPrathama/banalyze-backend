from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.modules.auth.auth_schema import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse, TokenSchema, RefreshTokenRequest
from app.modules.auth.auth_service import AuthService
from app.core.dependencies import get_current_user, get_current_user_refresh
from app.utils.responses import SuccessResponse, success_response
from typing import Any

router = APIRouter()

@router.post("/register", response_model=SuccessResponse[RegisterResponse], status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest, 
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    result = await auth_service.register_user(request)
    return success_response(data=result, message="User registered successfully")

@router.post("/login", response_model=SuccessResponse[LoginResponse])
async def login(
    request: LoginRequest, 
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    result = await auth_service.authenticate_user(request.email, request.password)
    return success_response(data=result, message="Login successful")

@router.post("/refreshToken", response_model=SuccessResponse[TokenSchema])
async def refresh_token(
    current_user: dict = Depends(get_current_user_refresh),
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)

    result = auth_service.create_tokens(str(current_user.id))
    return success_response(data=result, message="Tokens refreshed successfully")

@router.get("/me", response_model=SuccessResponse[dict[str, Any]])
async def get_me(current_user: dict = Depends(get_current_user)):
    user_data = {
        "id": str(current_user.id),
        "nama_user": current_user.nama_user,
        "email": current_user.email,
        "no_telephone": current_user.no_telephone,
        "avatar_url": current_user.avatar_url
    }
    return success_response(data=user_data, message="User profile retrieved successfully")
