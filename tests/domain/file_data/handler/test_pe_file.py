import io

import pytest
from botocore.response import StreamingBody

from domain.file_data.exception.pe_file import ExtractingFileError
from domain.file_data.handler.pe_file import PeFileHandler


class TestPeFileHandler:
    @pytest.mark.parametrize(
        "pe_file,arch,num_imports,num_exports,file_type",
        [
            (
                "/app/tests/fixtures/01nCLd7AG7XAlI0JH9G2E3rFbuahjIaD.dll",
                "x64",
                7,
                6,
                "dll",
            ),
            (
                "/app/tests/fixtures/4NJVWj81OrKmou0ndXnK5jdJgA09eQwQ.exe",
                "x32",
                21,
                0,
                "exe",
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_execute_with_valid_data(
        self, pe_file, arch, num_imports, num_exports, file_type
    ):
        pe_file_handler = PeFileHandler()
        with open(pe_file, "rb") as file:
            file_content = file.read()
        streaming_body = StreamingBody(io.BytesIO(file_content), len(file_content))
        pe_file_data = await pe_file_handler.execute(streaming_body)

        assert pe_file_data.file_type == file_type
        assert pe_file_data.arch == arch
        assert pe_file_data.num_imports == num_imports
        assert pe_file_data.num_exports == num_exports

    @pytest.mark.asyncio
    async def test_execute_with_invalid_data(self):
        pe_file_handler = PeFileHandler()
        file_content = b"invalid"
        streaming_body = StreamingBody(io.BytesIO(file_content), len(file_content))
        with pytest.raises(ExtractingFileError):
            await pe_file_handler.execute(streaming_body)
