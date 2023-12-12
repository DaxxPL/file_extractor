from datetime import datetime

from domain.file_data.model.file_sync_info import NotExtractedFile
from presistence.repository.mapper.fields.file import FileRepositoryFields


class FileSQLMapper:
    class Fields(FileRepositoryFields):
        pass

    @classmethod
    def map_to(cls, file: NotExtractedFile, sync_time: datetime) -> dict:
        _ = cls.Fields

        return {
            _.NAME: file.name,
            _.HASH: file.hash,
            _.SIZE: file.size,
            _.MALICIOUS: file.malicious,
            _.SYNC_TIME: sync_time.replace(tzinfo=None),
        }
