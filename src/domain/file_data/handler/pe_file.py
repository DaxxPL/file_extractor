import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

import pefile
from botocore.exceptions import BotoCoreError
from botocore.response import StreamingBody

from domain.file_data.exception.pe_file import ExtractingFileError
from domain.file_data.model.pe_file_data import PeFileData


logger = logging.getLogger(__name__)


class PeFileHandler:
    __slots__ = ("_pool",)

    def __init__(self) -> None:
        self._pool = ThreadPoolExecutor()

    async def execute(self, file_data: StreamingBody) -> PeFileData:
        try:
            pe = pefile.PE(
                data=await self.async_read_streaming_body(streaming_body=file_data),
                fast_load=True,
            )
            pe.parse_data_directories(
                directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"],
                ]
            )
        except (
            pefile.PEFormatError,
            BotoCoreError,
            IOError,
            asyncio.CancelledError,
        ) as error:
            logger.exception(error, exc_info=True)
            raise ExtractingFileError(
                f"Error: The file is not a valid PE file or is corrupted. {error}"
            )

        file_type = self._get_file_type(pe)
        arch = self._get_arch(pe)
        num_imports = self._get_number_of_imports(pe)
        num_exports = self._get_number_of_exports(pe)

        return PeFileData(
            file_type=file_type,
            arch=arch,
            num_imports=num_imports,
            num_exports=num_exports,
        )

    @classmethod
    def _get_file_type(cls, pe: pefile.PE) -> str:
        return "dll" if hasattr(pe, "DIRECTORY_ENTRY_EXPORT") else "exe"

    @classmethod
    def _get_arch(cls, pe: pefile.PE) -> str:
        arch = "x32"
        if (
            hasattr(pe, "FILE_HEADER")
            and pe.FILE_HEADER.Machine
            == pefile.MACHINE_TYPE["IMAGE_FILE_MACHINE_AMD64"]
        ):
            arch = "x64"
        return arch

    @classmethod
    def _get_number_of_imports(cls, pe: pefile.PE) -> int:
        return (
            len(pe.DIRECTORY_ENTRY_IMPORT)
            if hasattr(pe, "DIRECTORY_ENTRY_IMPORT")
            else 0
        )

    @classmethod
    def _get_number_of_exports(cls, pe: pefile.PE) -> int:
        return (
            len(pe.DIRECTORY_ENTRY_EXPORT.symbols)
            if hasattr(pe, "DIRECTORY_ENTRY_EXPORT")
            else 0
        )

    async def async_read_streaming_body(
        self, streaming_body: StreamingBody, chunk_size: int | None = None
    ) -> bytes:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(self._pool, streaming_body.read, chunk_size)
        return data
