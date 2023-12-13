from abc import ABC, abstractmethod
from io import IOBase
from typing import AsyncGenerator

from domain.file_data.model.file_sync_info import NotExtractedFile


class StorageServiceInterface(ABC):
    @abstractmethod
    async def paginate_by_prefix(
        self, prefix: str, page_size: int, malicious: bool
    ) -> AsyncGenerator[list[NotExtractedFile], None]:
        ...

    @abstractmethod
    async def get_streaming_body_by_key(self, file_key: str) -> IOBase:
        ...
