from pydantic_settings import BaseSettings


class WorkerSettings(BaseSettings):
    PGSQL_SERVER: str
    PGSQL_USER: str
    PGSQL_PASSWORD: str
    PGSQL_DATABASE: str
    PGSQL_PORT: int

    RESYNC_INTERVAL: int = 3600

    MAX_WORKERS: int = 10

    AWS_BUCKET_NAME: str

    SPARK_MASTER_URL: str
