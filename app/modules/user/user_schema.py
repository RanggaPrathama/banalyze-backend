from pydantic import BaseModel
from typing import Optional


class UpdateProfileRequest(BaseModel):
    nama_user: Optional[str] = None
    no_telephone: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: str
    nama_user: str
    email: str
    no_telephone: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}
