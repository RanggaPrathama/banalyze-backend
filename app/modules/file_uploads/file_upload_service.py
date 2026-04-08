from fastapi import UploadFile

from app.core.config import settings
from app.modules.file_uploads.base_storage import BaseStorageService


def _get_storage_backend() -> BaseStorageService:
    if settings.storage_backend == "supabase":
        from app.modules.file_uploads.supabase_storage import SupabaseStorageService
        return SupabaseStorageService()
    from app.modules.file_uploads.local_storage import LocalStorageService
    return LocalStorageService()


class FileUploadService:
    """
    Facade that delegates to the configured storage backend.
    Set STORAGE_BACKEND=supabase in .env to use Supabase Storage,
    or leave it as 'local' (default) for local filesystem storage.
    """

    def __init__(self) -> None:
        self._backend: BaseStorageService = _get_storage_backend()

    async def upload_image(self, file: UploadFile, folder: str) -> str:
        return await self._backend.upload_image(file, folder)

    async def delete_file(self, file_url: str) -> None:
        await self._backend.delete_file(file_url)

        