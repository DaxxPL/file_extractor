import datetime
import logging

from domain.file_data.repository.interface import FileRepositoryInterface
from domain.file_data.service.file_storage_service import StorageServiceInterface


logger = logging.getLogger(__name__)


class SyncCommand:
    def __init__(
        self,
        storage_service: StorageServiceInterface,
        file_repository: FileRepositoryInterface,
    ):
        self._storage_service = storage_service
        self._file_repository = file_repository

    async def execute(self, prefix: str, malicious: bool) -> None:
        sync_time = datetime.datetime.now(tz=datetime.timezone.utc)
        logger.info(f"Execution started with prefix: {prefix}, malicious: {malicious}")

        async for files in self._storage_service.paginate_by_prefix(
            prefix=prefix, malicious=malicious, page_size=1_000
        ):
            logger.info(f"Upserting {len(files)} files")
            await self._file_repository.upsert_many(files=files, sync_time=sync_time)
