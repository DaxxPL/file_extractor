from pydantic_settings import BaseSettings


class WorkerSettings(BaseSettings):
    PGSQL_SERVER: str
    PGSQL_USER: str
    PGSQL_PASSWORD: str
    PGSQL_DATABASE: str
    PGSQL_PORT: int

    AWS_BUCKET_NAME: str

    SPARK_MASTER_URL: str

    NUM_FILES: int = 1000
