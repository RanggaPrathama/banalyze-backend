from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import PyJWTError

from app.core.config import settings
from app.db import get_db
from app.modules.user.user_service import UserService

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: AsyncSession = Depends(get_db)
):
    
    print(r"Validating Access Token... : ", credentials.credentials)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        print("Decoded JWT Payload: ", payload)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
    
        if user_id is None or token_type != "access":
            raise credentials_exception
            
    except PyJWTError:
        raise credentials_exception
        
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_user_refresh(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: AsyncSession = Depends(get_db)
):
    """
    Guard khusus untuk memvalidasi Refresh Token dari Header Authorization Bearer.
    Digunakan secara eksklusif pada endpoint POST /refresh
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Dekode menggunakan jwt_refresh_secret_key
        payload = jwt.decode(
            credentials.credentials, 
            settings.jwt_refresh_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        # Validasi tambahan, token benar-benar berjenis "refresh"
        if user_id is None or token_type != "refresh":
            raise credentials_exception
            
    except PyJWTError:
        raise credentials_exception
        
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if user is None:
        raise credentials_exception
        
    return user
