from datetime import datetime, timezone

# import mocks from pytest
from unittest.mock import Mock, patch

import pytest
from pyspark.sql import Row, SparkSession

from domain.file_data.command.extract import ExtractCommand
from presistence.repository.mapper.fields.file import FileRepositoryFields


def create_test_spark_session() -> SparkSession:
    return SparkSession.builder.master("local[1]").appName("PySparkTest").getOrCreate()


@pytest.fixture(scope="module")
def spark_session() -> SparkSession:
    return create_test_spark_session()


@pytest.fixture
def mock_storage_service() -> Mock:
    return Mock()


@pytest.fixture
def mock_file_repository() -> Mock:
    return Mock()


@pytest.fixture
def mock_psql_settings() -> Mock:
    return Mock()


@pytest.fixture
def extract_command(
    mock_storage_service: Mock, mock_file_repository: Mock, mock_psql_settings: Mock
):
    return ExtractCommand(
        file_repository=mock_file_repository,
        storage_service=mock_storage_service,
        psql_settings=mock_psql_settings,
        source_table="source_table",
        target_table="target_table",
        spark_url="local",
        db_table_fields=FileRepositoryFields,
    )


class TestExtractCommand:
    def test_extract_unprocessed_files_when_there_is_processed_file(
        self, spark_session: SparkSession, extract_command: ExtractCommand
    ):
        # Given
        source_data = [
            Row(
                name="name1",
                hash="hash1",
                size=1,
                malicious=True,
                sync_time=datetime.now(timezone.utc),
            ),
            Row(
                name="name2",
                hash="hash2",
                size=2,
                malicious=True,
                sync_time=datetime.now(timezone.utc),
            ),
        ]
        target_data = [
            Row(
                name="name1",
                hash="hash1",
                size=1,
                malicious=True,
                architecture="x64",
                num_imports=1,
                num_exports=1,
                status="EXTRACTED",
                created_at=datetime.now(timezone.utc),
            ),
        ]

        source_df = spark_session.createDataFrame(source_data)
        target_df = spark_session.createDataFrame(target_data)

        # When
        unprocessed_files_df = extract_command._extract_unprocessed_files(
            storage_df=source_df, extracted_df=target_df, malicious=True, num_files=1
        )

        # Then
        assert unprocessed_files_df.count() == 1
        assert unprocessed_files_df.first().name == "name2"
        assert unprocessed_files_df.first().hash == "hash2"

    def test_extract_unprocessed_files_when_there_is_no_processed_file(
        self, spark_session: SparkSession, extract_command: ExtractCommand
    ):
        # Given
        source_data = [
            Row(
                name="name1",
                hash="hash1",
                size=1,
                malicious=True,
                sync_time=datetime.now(timezone.utc),
            ),
            Row(
                name="name2",
                hash="hash2",
                size=2,
                malicious=True,
                sync_time=datetime.now(timezone.utc),
            ),
        ]
        target_data = []

        source_df = spark_session.createDataFrame(source_data)
        target_df = spark_session.createDataFrame(target_data, extract_command._schema)

        # When
        unprocessed_files_df = extract_command._extract_unprocessed_files(
            storage_df=source_df, extracted_df=target_df, malicious=True, num_files=2
        )

        # Then
        assert unprocessed_files_df.count() == 2

    def test_get_unique_rows_with_matching_hashes(
        self, spark_session: SparkSession, extract_command: ExtractCommand
    ):
        # Given
        source_data = [
            Row(
                name="name1",
                hash="hash1",
                size=1,
                malicious=True,
                sync_time=datetime.now(timezone.utc),
            ),
            Row(
                name="name2",
                hash="hash1",
                size=1,
                malicious=True,
                sync_time=datetime.now(timezone.utc),
            ),
        ]

        target_data = [
            Row(
                name="name1",
                hash="hash1",
                size=1,
                malicious=True,
                architecture="x64",
                num_imports=1,
                num_exports=1,
                status="EXTRACTED",
                created_at=datetime.now(timezone.utc),
            ),
            Row(
                name="name2",
                hash="hash2",
                size=2,
                malicious=True,
                architecture="x64",
                num_imports=1,
                num_exports=1,
                status="EXTRACTED",
                created_at=datetime.now(timezone.utc),
            ),
        ]

        source_df = spark_session.createDataFrame(source_data)
        target_df = spark_session.createDataFrame(target_data)

        # When
        matching_rows_df = (
            extract_command._get_unique_extracted_rows_with_matching_hashes(
                unprocessed_files_df=source_df, extracted_df=target_df
            )
        )

        # Then
        assert matching_rows_df.count() == 1
        assert matching_rows_df.first().name == "name1"
        assert matching_rows_df.first().hash == "hash1"

    def test_join_unprocessed_and_matched_data(
        self, spark_session: SparkSession, extract_command: ExtractCommand
    ):
        # Given

        unprocessed_files_data = [
            Row(
                name="name1",
                hash="hash1",
                size=1,
                malicious=True,
                sync_time=datetime.now(timezone.utc),
            ),
            Row(
                name="name2",
                hash="hash2",
                size=2,
                malicious=True,
                sync_time=datetime.now(timezone.utc),
            ),
        ]

        matching_rows_data = [
            Row(
                name="name1",
                hash="hash1",
                size=1,
                malicious=True,
                architecture="x64",
                num_imports=1,
                num_exports=1,
                status="EXTRACTED",
                created_at=datetime.now(timezone.utc),
            ),
        ]

        unprocessed_files_df = spark_session.createDataFrame(unprocessed_files_data)
        matching_rows_df = spark_session.createDataFrame(matching_rows_data)

        # When

        unprocessed_files_matching_rows_df = (
            extract_command._join_unprocessed_and_matched_data(
                unprocessed_files_df=unprocessed_files_df,
                matching_rows_df=matching_rows_df,
            )
        )

        # Then

        assert unprocessed_files_matching_rows_df.count() == 1
        assert unprocessed_files_matching_rows_df.first().name == "name1"
        assert unprocessed_files_matching_rows_df.first().hash == "hash1"
        assert unprocessed_files_matching_rows_df.first().architecture == "x64"
        assert unprocessed_files_matching_rows_df.first().num_imports == 1
        assert unprocessed_files_matching_rows_df.first().num_exports == 1
        assert unprocessed_files_matching_rows_df.first().status == "EXTRACTED"
        assert unprocessed_files_matching_rows_df.first().created_at is not None

    def test_get_unprocessed_files(
        self, spark_session: SparkSession, extract_command: ExtractCommand
    ):
        # Given

        unprocessed_files_data = [
            Row(
                name="name1",
                hash="hash1",
                size=1,
                malicious=True,
                sync_time=datetime.now(timezone.utc),
            ),
            Row(
                name="name2",
                hash="hash2",
                size=2,
                malicious=True,
                sync_time=datetime.now(timezone.utc),
            ),
        ]

        unprocessed_files_matching_rows_data = [
            Row(
                name="name1",
                hash="hash1",
                size=1,
                malicious=True,
                architecture="x64",
                num_imports=1,
                num_exports=1,
                status="EXTRACTED",
                created_at=datetime.now(timezone.utc),
            ),
        ]

        unprocessed_files_df = spark_session.createDataFrame(unprocessed_files_data)
        unprocessed_files_matching_rows_df = spark_session.createDataFrame(
            unprocessed_files_matching_rows_data
        )

        # When

        unprocessed_files_df = extract_command._get_unprocessed_files(
            unprocessed_files_df=unprocessed_files_df,
            unprocessed_files_matching_rows_df=unprocessed_files_matching_rows_df,
        )

        # Then

        assert unprocessed_files_df.count() == 1
        assert unprocessed_files_df.first().name == "name2"
        assert unprocessed_files_df.first().hash == "hash2"

    def test_process_distinct_files_and_update_metadata(
        self, spark_session: SparkSession, extract_command: ExtractCommand
    ):
        # Given

        unprocessed_files_data = [
            Row(
                name="name1",
                hash="hash1",
                size=1,
                malicious=True,
                sync_time=datetime.now(timezone.utc),
            ),
            Row(
                name="name2",
                hash="hash2",
                size=2,
                malicious=True,
                sync_time=datetime.now(timezone.utc),
            ),
        ]

        unprocessed_files_df = spark_session.createDataFrame(unprocessed_files_data)

        # When

        with patch(
            "domain.file_data.command.extract.download_and_extract_multiple_file_data"
        ) as mock_download_and_extract_multiple_file_data:
            mock_download_and_extract_multiple_file_data.return_value = [
                Row(
                    name="name1",
                    hash="hash1",
                    size=1,
                    architecture="x32",
                    num_imports=0,
                    num_exports=0,
                    status="EXTRACTED",
                    malicious=True,
                    created_at=datetime.now(timezone.utc),
                ),
                Row(
                    name="name2",
                    hash="hash2",
                    size=2,
                    architecture="x32",
                    num_imports=0,
                    num_exports=0,
                    status="EXTRACTED",
                    malicious=True,
                    created_at=datetime.now(timezone.utc),
                ),
            ]
            processed_files_df = (
                extract_command._process_distinct_files_and_update_metadata(
                    unprocessed_files_df=unprocessed_files_df, spark=spark_session
                )
            )

        # Then

        assert processed_files_df.count() == 2
        assert processed_files_df.first().name == "name1"
        assert processed_files_df.first().hash == "hash1"
        assert processed_files_df.first().size == 1
        assert processed_files_df.first().architecture == "x32"
        assert processed_files_df.first().num_imports == 0
        assert processed_files_df.first().num_exports == 0
        assert processed_files_df.first().status == "EXTRACTED"
        assert processed_files_df.first().malicious is True
        assert processed_files_df.first().created_at is not None
