from abc import ABC, abstractmethod
from typing import Optional


class StorageService(ABC):
    @abstractmethod
    async def upload_file(self, file_data: bytes, filename: str, content_type: str) -> str:
        pass

    @abstractmethod
    async def delete_file(self, file_url: str) -> bool:
        pass

    @abstractmethod
    async def get_file_url(self, filename: str) -> str:
        pass


class LocalStorageService(StorageService):
    def __init__(self, base_path: str = "uploads/"):
        self.base_path = base_path
        import os
        os.makedirs(base_path, exist_ok=True)

    async def upload_file(self, file_data: bytes, filename: str, content_type: str) -> str:
        import os
        file_path = os.path.join(self.base_path, filename)
        with open(file_path, "wb") as f:
            f.write(file_data)
        return f"/uploads/{filename}"

    async def delete_file(self, file_url: str) -> bool:
        import os
        file_path = file_url.replace("/uploads/", self.base_path)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    async def get_file_url(self, filename: str) -> str:
        return f"/uploads/{filename}"


def get_storage_service() -> StorageService:
    return LocalStorageService()
