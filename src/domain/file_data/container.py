from functools import cached_property

from common.pgsql import PgsqlSettings
from domain.file_data.command.extract import ExtractCommand
from domain.file_data.command.sync import SyncCommand
from domain.file_data.repository.interface import FileRepositoryInterface
from domain.file_data.service.file_storage_service import StorageServiceInterface


class FileDataContainer:
    storage_service: StorageServiceInterface
    file_repository: FileRepositoryInterface
    pgsql_settings: PgsqlSettings

    @cached_property
    def sync_command(self) -> SyncCommand:
        return SyncCommand(
            storage_service=self.storage_service, file_repository=self.file_repository
        )

    @cached_property
    def extract_command(self) -> ExtractCommand:
        return ExtractCommand(
            file_repository=self.file_repository,
            storage_service=self.storage_service,
            psql_settings=self.pgsql_settings,
            source_table="storage_file_metadata",
            target_table="extracted_file_metadata",
        )
