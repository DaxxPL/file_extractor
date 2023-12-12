import asyncio
import datetime
import logging

from pyspark import Row

from common.settings import WorkerSettings
from domain.file_data.exception.pe_file import ExtractingFileError
from domain.file_data.handler.pe_file import PeFileHandler
from presistence.service.s3 import S3FileService


logger = logging.getLogger(__name__)


async def download_and_extract_file_data(file_row: Row) -> Row:
    settings = WorkerSettings()
    s3_file_service = S3FileService(bucket_name=settings.AWS_BUCKET_NAME)
    pe_file_handler = PeFileHandler()
    file_obj = await s3_file_service.get_streaming_body_by_key(file_key=file_row.name)

    try:
        pe_file_data = await pe_file_handler.execute(file_data=file_obj)

    except ExtractingFileError as error:
        logger.error(error, exc_info=True)
        return Row(
            name=file_row.name,
            hash=file_row.hash,
            size=file_row.size,
            architecture=None,
            num_imports=None,
            num_exports=None,
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
        status="EXTRACTED",
        malicious=file_row.malicious,
        created_at=datetime.datetime.now(tz=datetime.timezone.utc),
    )


async def download_and_extract_multiple_file_data_async(
    file_rows: list[Row],
) -> list[Row]:
    tasks = [download_and_extract_file_data(file_row) for file_row in file_rows]
    return await asyncio.gather(*tasks)


def download_and_extract_multiple_file_data(file_rows: list[Row]) -> list[Row]:
    return asyncio.run(download_and_extract_multiple_file_data_async(file_rows))
