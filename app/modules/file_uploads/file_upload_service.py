import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException, status

from app.core.config import settings

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MIME_TO_EXT = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
BASE_UPLOAD_DIR = "uploads"


class FileUploadService:

    async def upload_image(self, file: UploadFile, folder: str) -> str:
        """
        Validates and saves an image file into uploads/<folder>/.

        Args:
            file   : The uploaded file (UploadFile from FastAPI).
            folder : Sub-directory name under uploads/ e.g. "avatars", "history".

        Returns:
            Full public URL: <base_url>/static/<folder>/<uuid>.<ext>
        """
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

        # --- Ensure target directory exists ---
        upload_dir = os.path.join(BASE_UPLOAD_DIR, folder)
        os.makedirs(upload_dir, exist_ok=True)

        # --- Generate safe unique filename ---
        ext = MIME_TO_EXT[file.content_type]
        filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(upload_dir, filename)

        # --- Persist file asynchronously ---
        async with aiofiles.open(file_path, "wb") as out:
            await out.write(content)

        # --- Build and return full public URL ---
        base_url = settings.base_url.rstrip("/")
        return f"{base_url}/static/{folder}/{filename}"

    async def delete_file(self, file_url: str):
        """
        Deletes a file from the filesystem based on its public URL.

        Args:
            file_url: The full public URL of the file to delete.
        """
        base_url = settings.base_url.rstrip("/")
        if not file_url.startswith(f"{base_url}/static/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file URL. Must start with base URL + /static/."
            )
        
        # Extract the relative path after /static/
        relative_path = file_url[len(f"{base_url}/static/"):]
        file_path = os.path.join(BASE_UPLOAD_DIR, relative_path)

        # Ensure the file is within the uploads directory
        if not os.path.commonpath([os.path.abspath(file_path), os.path.abspath(BASE_UPLOAD_DIR)]) == os.path.abspath(BASE_UPLOAD_DIR):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path. Must be within the uploads directory."
            )

        # Delete the file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found."
            )
        
        