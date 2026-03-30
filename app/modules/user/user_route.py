import importlib.util
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db import get_db
from app.modules.user.user_schema import UpdateProfileRequest, UserProfileResponse
from app.modules.user.user_service import UserService
from app.utils.responses import SuccessResponse, success_response


router = APIRouter()

@router.put("/profile", response_model=SuccessResponse[UserProfileResponse])
async def update_profile(
    request: UpdateProfileRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update profile data (nama_user, no_telephone)."""
    data = request.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update.",
        )

    user_service = UserService(db)
    user = await user_service.update_profile(str(current_user.id), data)

    return success_response(
        data=UserProfileResponse(
            id=str(user.id),
            nama_user=user.nama_user,
            email=user.email,
            no_telephone=user.no_telephone,
            avatar_url=user.avatar_url,
        ),
        message="Profile updated successfully.",
    )


@router.put("/profile/avatar", response_model=SuccessResponse[UserProfileResponse])
async def update_avatar(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.update_avatar(str(current_user.id), file)

    return success_response(
        data=UserProfileResponse(
            id=str(user.id),
            nama_user=user.nama_user,
            email=user.email,
            no_telephone=user.no_telephone,
            avatar_url=user.avatar_url,
        ),
        message="Avatar updated successfully.",
    )
