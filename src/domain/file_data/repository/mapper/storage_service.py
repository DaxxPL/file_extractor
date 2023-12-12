from domain.file_data.model.file_sync_info import NotExtractedFile


class StorageServiceFileMapper:
    @staticmethod
    def to_domain(s3_file: dict, malicious: bool) -> NotExtractedFile:
        return NotExtractedFile(
            name=s3_file["Key"],
            hash=s3_file["ETag"].strip('"'),
            size=s3_file["Size"],
            malicious=malicious,
        )
