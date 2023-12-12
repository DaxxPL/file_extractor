import io

import pytest
from botocore.response import StreamingBody

from domain.file_data.handler.pe_file import PeFileHandler


class TestPeFileHandler:
    @pytest.fixture
    def pe_file_handler(self):
        return PeFileHandler()

    @pytest.mark.asyncio
    async def test_execute_with_real_data(self, pe_file_handler):
        with open(
            "/app/tests/fixtures/01nCLd7AG7XAlI0JH9G2E3rFbuahjIaD.dll", "rb"
        ) as file:
            file_content = file.read()
        streaming_body = StreamingBody(io.BytesIO(file_content), len(file_content))
        pe_file_data = await pe_file_handler.execute(streaming_body)

        assert pe_file_data.file_type == "dll"
        assert pe_file_data.arch == "x64"
        assert pe_file_data.num_imports == 69
        assert pe_file_data.num_exports == 14
