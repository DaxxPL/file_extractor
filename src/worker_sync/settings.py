from pydantic_settings import BaseSettings


class SyncWorkerSettings(BaseSettings):
    PGSQL_SERVER: str
    PGSQL_USER: str
    PGSQL_PASSWORD: str
    PGSQL_DATABASE: str
    PGSQL_PORT: int

    RESYNC_INTERVAL: int = 3600

    AWS_BUCKET_NAME: str
