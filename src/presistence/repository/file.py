import datetime
import logging

from common.pgsql import PSQLDatabase
from domain.file_data.model.file_sync_info import NotExtractedFile
from domain.file_data.repository.interface import FileRepositoryInterface
from presistence.repository.mapper.fields.file import FileRepositoryFields
from presistence.repository.mapper.file import FileSQLMapper


logger = logging.getLogger(__name__)


class PgSqlFileRepository(FileRepositoryInterface):
    def __init__(
        self,
        table: str,
        psql_database: PSQLDatabase,
    ):
        self._table = table
        self._psql_database = psql_database

    async def upsert_many(
        self, files: list[NotExtractedFile], sync_time: datetime.datetime
    ) -> None:
        _ = FileRepositoryFields
        mapped_files = [
            FileSQLMapper.map_to(file=file, sync_time=sync_time) for file in files
        ]

        async with self._psql_database.pool.acquire() as connection:
            async with connection.transaction():
                await connection.executemany(
                    f"""
                    INSERT INTO
                    {self._table}
                    ({_.NAME}, {_.HASH}, {_.SIZE}, {_.MALICIOUS}, {_.SYNC_TIME})
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT ({_.NAME}, {_.HASH})
                    DO UPDATE SET
                        {_.SYNC_TIME} = EXCLUDED.{_.SYNC_TIME}
                    """,
                    [
                        (
                            file[_.NAME],
                            file[_.HASH],
                            file[_.SIZE],
                            file[_.MALICIOUS],
                            file[_.SYNC_TIME],
                        )
                        for file in mapped_files
                    ],
                )
