import asyncio
import datetime
import logging
from typing import Iterator

from pyspark import Row

from common.settings import WorkerSettings
from domain.file_data.exception.pe_file import ExtractingFileError
from domain.file_data.handler.pe_file import PeFileHandler
from presistence.service.s3 import S3FileService


logger = logging.getLogger(__name__)


class FileProcessor:
    def __init__(self, s3_file_service: S3FileService, pe_file_handler: PeFileHandler):
        self._s3_file_service = s3_file_service
        self._pe_file_handler = pe_file_handler

    async def _download_and_extract_file_data(self, file_row: Row) -> Row:
        file_obj = await self._s3_file_service.get_streaming_body_by_key(
            file_key=file_row.name
        )

        try:
            pe_file_data = await self._pe_file_handler.execute(file_data=file_obj)

        except ExtractingFileError as error:
            logger.error(error, exc_info=True)
            return Row(
                name=file_row.name,
                hash=file_row.hash,
                size=file_row.size,
                architecture=None,
                num_imports=None,
                num_exports=None,
                type=None,
                status="ERROR",
                malicious=file_row.malicious,
                created_at=datetime.datetime.now(tz=datetime.timezone.utc),
            )

        return Row(
            name=file_row.name,
            hash=file_row.hash,
            size=file_row.size,
            architecture=pe_file_data.arch,
            num_imports=pe_file_data.num_imports,
            num_exports=pe_file_data.num_exports,
            type=pe_file_data.file_type,
            status="EXTRACTED",
            malicious=file_row.malicious,
            created_at=datetime.datetime.now(tz=datetime.timezone.utc),
        )

    async def _process_files_async(self, file_rows: list[Row]) -> list[Row]:
        tasks = [
            self._download_and_extract_file_data(file_row) for file_row in file_rows
        ]
        return await asyncio.gather(*tasks)

    def execute(self, file_rows: list[Row]) -> list[Row]:
        return asyncio.run(self._process_files_async(file_rows))


def process_partition(partition: Iterator[Row]) -> list[Row]:
    settings = WorkerSettings()
    processor = FileProcessor(
        s3_file_service=S3FileService(bucket_name=settings.AWS_BUCKET_NAME),
        pe_file_handler=PeFileHandler(),
    )
    return processor.execute(list(partition))
