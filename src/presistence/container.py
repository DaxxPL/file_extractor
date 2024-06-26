from functools import cached_property

from common.pgsql import PSQLDatabase
from common.settings import WorkerSettings
from presistence.repository.file import PgSqlFileRepository
from presistence.service.s3 import S3FileService


class PersistentLayerContainer:
    database: PSQLDatabase
    settings: WorkerSettings

    @cached_property
    def storage_service(self) -> S3FileService:
        return S3FileService(
            bucket_name=self.settings.AWS_BUCKET_NAME,
        )

    @cached_property
    def file_repository(self) -> PgSqlFileRepository:
        return PgSqlFileRepository(
            psql_database=self.database, table="storage_file_metadata"
        )
