from functools import cached_property

from common.pgsql import PgsqlSettings, PSQLDatabase
from domain.file_data.container import FileDataContainer
from presistence.container import PersistentLayerContainer
from worker_sync.settings import SyncWorkerSettings


class SyncWorkerContainer(PersistentLayerContainer, FileDataContainer):
    def __init__(self, settings: SyncWorkerSettings):
        self.settings = settings

    @cached_property
    def pgsql_settings(self) -> PgsqlSettings:
        return PgsqlSettings(
            host=self.settings.PGSQL_SERVER,
            port=self.settings.PGSQL_PORT,
            database=self.settings.PGSQL_DATABASE,
            user=self.settings.PGSQL_USER,
            password=self.settings.PGSQL_PASSWORD,
        )

    @cached_property
    def database(self) -> PSQLDatabase:
        return PSQLDatabase(self.pgsql_settings)

    async def close(self) -> None:
        await self.database.pool.close()
