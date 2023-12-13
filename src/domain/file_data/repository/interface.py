from abc import ABC, abstractmethod
from datetime import datetime

from domain.file_data.model.file_sync_info import NotExtractedFile


class FileRepositoryInterface(ABC):
    ...

    @abstractmethod
    async def upsert_many(
        self,
        files: list[NotExtractedFile],
        sync_time: datetime,
    ) -> None:
        ...
