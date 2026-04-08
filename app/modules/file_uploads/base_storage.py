from abc import ABC, abstractmethod
from fastapi import UploadFile


class BaseStorageService(ABC):

    @abstractmethod
    async def upload_image(self, file: UploadFile, folder: str) -> str:
        """
        Upload an image file to the storage backend.

        Args:
            file   : The uploaded file (UploadFile from FastAPI).
            folder : Sub-directory / prefix e.g. "avatars", "history_classify".

        Returns:
            Public URL string of the uploaded file.
        """
        ...

    @abstractmethod
    async def delete_file(self, file_url: str) -> None:
        """
        Delete a file from the storage backend by its public URL.

        Args:
            file_url: The public URL previously returned by upload_image.
        """
        ...
