import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, AsyncGenerator

import boto3
from botocore import UNSIGNED
from botocore.client import Config
from botocore.response import StreamingBody

from domain.file_data.model.file_sync_info import NotExtractedFile
from domain.file_data.repository.mapper.storage_service import StorageServiceFileMapper
from domain.file_data.service.file_storage_service import StorageServiceInterface


class S3FileService(StorageServiceInterface):
    def __init__(self, bucket_name: str):
        self.pool = ThreadPoolExecutor()
        self._client = boto3.client("s3", config=Config(signature_version=UNSIGNED))
        self._bucket_name = bucket_name

    async def paginate_by_prefix(
        self,
        prefix: str,
        malicious: bool,
        page_size: int = 1_000,
    ) -> AsyncGenerator[list[NotExtractedFile], None]:
        loop = asyncio.get_event_loop()
        paginator = self._client.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(
            Bucket=self._bucket_name,
            Prefix=prefix,
            PaginationConfig={"PageSize": page_size},
        )

        def get_page(page: dict[str, Any]) -> list[NotExtractedFile]:
            return [
                StorageServiceFileMapper.to_domain(s3_file=s3_file, malicious=malicious)
                for s3_file in page["Contents"]
            ]

        for page in page_iterator:
            result = await loop.run_in_executor(self.pool, get_page, page)
            yield result

    async def get_streaming_body_by_key(self, file_key: str) -> StreamingBody:
        loop = asyncio.get_event_loop()
        file_obj = await loop.run_in_executor(self.pool, self._get_object, file_key)
        return file_obj["Body"]

    def _get_object(self, file_key: str) -> dict[str, Any]:
        return self._client.get_object(Bucket=self._bucket_name, Key=file_key)
