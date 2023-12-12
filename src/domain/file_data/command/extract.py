import logging

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, current_timestamp
from pyspark.sql.types import (
    BooleanType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from common.pgsql import PgsqlSettings
from domain.file_data.file_extraction import download_and_extract_multiple_file_data
from domain.file_data.repository.interface import FileRepositoryInterface
from domain.file_data.service.file_storage_service import StorageServiceInterface


logger = logging.getLogger(__name__)


class ExtractCommand:
    def __init__(
        self,
        file_repository: FileRepositoryInterface,
        storage_service: StorageServiceInterface,
        psql_settings: PgsqlSettings,
        source_table: str,
        target_table: str,
        spark_url: str,
    ):
        self._file_repository = file_repository
        self._storage_service = storage_service
        self._psql_settings = psql_settings
        self._jbdc_url = (
            f"jdbc:postgresql://{self._psql_settings.host}:"
            f"{self._psql_settings.port}/{self._psql_settings.database}"
        )
        self._spark_url = spark_url
        self._source_table = source_table
        self._target_table = target_table
        self._schema = StructType(
            [
                StructField("name", StringType(), False),
                StructField("hash", StringType(), False),
                StructField("size", IntegerType(), False),
                StructField("architecture", StringType(), True),
                StructField("num_imports", IntegerType(), True),
                StructField("num_exports", IntegerType(), True),
                StructField("status", StringType(), False),
                StructField("malicious", BooleanType(), False),
                StructField("created_at", TimestampType(), False),
            ]
        )

    def execute(self, malicious: bool, num_files: int) -> None:
        spark = self._create_spark_session()

        storage_df = self._load_data(spark=spark, table_name=self._source_table)
        extracted_df = self._load_data(spark=spark, table_name=self._target_table)

        unprocessed_files_df = self._extract_unprocessed_files(
            storage_df=storage_df,
            extracted_df=extracted_df,
            malicious=malicious,
            num_files=num_files,
        )

        matching_rows_df = self._get_unique_rows_with_matching_hashes(
            unprocessed_files_df=unprocessed_files_df, extracted_df=extracted_df
        )

        unprocessed_files_matching_rows_df = self._join_unprocessed_and_matched_data(
            unprocessed_files_df=unprocessed_files_df,
            matching_rows_df=matching_rows_df,
        )

        unprocessed_files_df = self._get_unprocessed_files(
            unprocessed_files_df=unprocessed_files_df,
            unprocessed_files_matching_rows_df=unprocessed_files_matching_rows_df,
        )

        if unprocessed_files_df.count() == 0:
            logger.info("No files to extract")
            return

        processed_files_df = self._process_distinct_files_and_update_metadata(
            unprocessed_files_df=unprocessed_files_df, spark=spark
        )
        self._write_to_database(dataframe=processed_files_df)
        self._write_to_database(dataframe=unprocessed_files_matching_rows_df)

    def _create_spark_session(self) -> SparkSession:
        return (
            SparkSession.builder.appName("BinaryFileProcessor")
            .master(self._spark_url)
            .getOrCreate()
        )

    def _load_data(self, spark: SparkSession, table_name: str) -> DataFrame:
        return (
            spark.read.format("jdbc")
            .option("url", self._jbdc_url)
            .option("dbtable", table_name)
            .option("user", self._psql_settings.user)
            .option("password", self._psql_settings.password)
            .load()
        )

    @staticmethod
    def _extract_unprocessed_files(
        storage_df: DataFrame, extracted_df: DataFrame, malicious: bool, num_files: int
    ) -> DataFrame:
        storage_filtered_df = storage_df.filter(col("malicious") == malicious)

        df_result = storage_filtered_df.join(
            extracted_df,
            (storage_df["name"] == extracted_df["name"])
            & (storage_df["hash"] == extracted_df["hash"]),
            "left_anti",
        )

        first_files_df = df_result.limit(num_files)
        return first_files_df

    def _get_unique_rows_with_matching_hashes(
        self, unprocessed_files_df: DataFrame, extracted_df: DataFrame
    ) -> DataFrame:
        unprocessed_distinct_hashes_df = unprocessed_files_df.select("hash").distinct()
        unprocessed_distinct_hashes_list = [
            row["hash"] for row in unprocessed_distinct_hashes_df.collect()
        ]
        unique_extracted_rows_df = extracted_df.filter(
            extracted_df["hash"].isin(unprocessed_distinct_hashes_list)
        ).dropDuplicates(["hash"])

        return unique_extracted_rows_df

    def _join_unprocessed_and_matched_data(
        self, unprocessed_files_df: DataFrame, matching_rows_df: DataFrame
    ) -> DataFrame:
        unprocessed_files_df_alias = unprocessed_files_df.alias("a")
        matching_rows_df_alias = matching_rows_df.alias("b")

        return unprocessed_files_df_alias.join(
            matching_rows_df_alias,
            col("a.hash") == col("b.hash"),
            "inner",
        ).select(
            col("a.name"),
            col("b.hash"),
            col("b.size"),
            col("b.architecture"),
            col("b.num_imports"),
            col("b.num_exports"),
            col("b.status"),
            col("b.malicious"),
            current_timestamp().alias("created_at"),
        )

    def _get_unprocessed_files(
        self,
        unprocessed_files_df: DataFrame,
        unprocessed_files_matching_rows_df: DataFrame,
    ) -> DataFrame:
        return unprocessed_files_df.join(
            unprocessed_files_matching_rows_df,
            ["hash"],
            "left_anti",
        )

    def _process_distinct_files_and_update_metadata(
        self, unprocessed_files_df: DataFrame, spark: SparkSession
    ) -> DataFrame:
        distinct_files_df = unprocessed_files_df.dropDuplicates(["hash"])
        distinct_files_rdd = distinct_files_df.rdd

        extracted_data = distinct_files_rdd.mapPartitions(
            download_and_extract_multiple_file_data
        )
        extracted_data_df = spark.createDataFrame(
            extracted_data.filter(lambda x: x is not None), self._schema
        )
        extracted_data_df = extracted_data_df.alias("a")
        unprocessed_files_df = unprocessed_files_df.alias("b")

        final_metadata_df = unprocessed_files_df.join(
            extracted_data_df, "hash", "left"
        ).select(
            col("b.name"),
            col("a.hash"),
            col("a.size"),
            col("a.architecture"),
            col("a.num_imports"),
            col("a.num_exports"),
            col("a.status"),
            col("a.malicious"),
            current_timestamp().alias("created_at"),
        )
        return final_metadata_df

    def _write_to_database(self, dataframe: DataFrame) -> None:
        dataframe.write.jdbc(
            url=self._jbdc_url,
            table=self._target_table,
            mode="append",
            properties={
                "user": self._psql_settings.user,
                "password": self._psql_settings.password,
            },
        )
