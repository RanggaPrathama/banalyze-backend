import uuid
from fastapi import UploadFile, HTTPException, status
from supabase import AsyncClient, acreate_client

from app.core.config import settings
from app.modules.file_uploads.base_storage import BaseStorageService

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MIME_TO_EXT = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB


class SupabaseStorageService(BaseStorageService):

    async def _get_client(self) -> AsyncClient:
        return await acreate_client(settings.supabase_url, settings.supabase_key)

    async def upload_image(self, file: UploadFile, folder: str) -> str:
        # --- Validate content type ---
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"File type '{file.content_type}' is not allowed. "
                    "Accepted types: image/jpeg, image/png, image/webp."
                ),
            )

        # --- Validate extension (double-check against filename) ---
        if file.filename:
            ext_from_name = file.filename.rsplit(".", 1)[-1].lower()
            if ext_from_name not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"File extension '.{ext_from_name}' is not allowed. "
                        "Accepted extensions: .jpg, .jpeg, .png, .webp."
                    ),
                )

        # --- Read and validate file size ---
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"File size ({len(content) / (1024 * 1024):.2f} MB) "
                    "exceeds the maximum allowed size of 2 MB."
                ),
            )

        # --- Generate safe unique path ---
        ext = MIME_TO_EXT[file.content_type]
        filename = f"{uuid.uuid4()}.{ext}"
        object_path = f"{folder}/{filename}"

        # --- Upload to Supabase Storage ---
        client = await self._get_client()
        try:
            await client.storage.from_(settings.supabase_bucket).upload(
                path=object_path,
                file=content,
                file_options={"content-type": file.content_type},
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to storage: {str(e)}",
            )

        # --- Build and return public URL ---
        public_url = await client.storage.from_(settings.supabase_bucket).get_public_url(object_path)
        return public_url

    async def delete_file(self, file_url: str) -> None:
        # Extract object path from the public URL
        # Supabase public URL format: <supabase_url>/storage/v1/object/public/<bucket>/<path>
        bucket_prefix = f"/storage/v1/object/public/{settings.supabase_bucket}/"
        if bucket_prefix not in file_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Supabase file URL.",
            )

        object_path = file_url.split(bucket_prefix, 1)[1]

        client = await self._get_client()
        try:
            await client.storage.from_(settings.supabase_bucket).remove([object_path])
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file from storage: {str(e)}",
            )
