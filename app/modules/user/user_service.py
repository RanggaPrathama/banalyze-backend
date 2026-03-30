from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import cast, String
from app.models.user import User
from app.modules.file_uploads import FileUploadService
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.file_upload_service = FileUploadService()

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()
        
    async def get_user_by_id(self, user_id: str) -> User | None:
        result = await self.db.execute(select(User).where(cast(User.id, String) == str(user_id)))
        return result.scalars().first()

    async def create_user(self, user_data: dict) -> User:
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_profile(self, user_id: str, data: dict) -> User | None:
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        for key, value in data.items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_avatar(self, user_id: str, avatar_file: UploadFile) -> User | None:
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        if user.avatar_url:
            await self.file_upload_service.delete_file(user.avatar_url)

        avatar_url = await self.file_upload_service.upload_image(avatar_file, folder="avatars")

        user.avatar_url = avatar_url
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    
