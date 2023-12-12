from abc import ABC, abstractmethod
from typing import AsyncGenerator

from domain.file_data.model.file_sync_info import NotExtractedFile


class StorageServiceInterface(ABC):
    @abstractmethod
    async def paginate_by_prefix(
        self, prefix: str, page_size: int, malicious: bool
    ) -> AsyncGenerator[list[NotExtractedFile], None]:
        ...
