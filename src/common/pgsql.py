import logging
from dataclasses import dataclass

import asyncpg


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class PgsqlSettings:
    host: str
    port: int
    database: str
    user: str
    password: str


class PSQLDatabase:
    __slots__ = ("pgsql_settings", "pool")

    def __init__(self, pgsql_settings: PgsqlSettings):
        self.pgsql_settings = pgsql_settings
        self.pool = None

    async def initialize(self) -> None:
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                host=self.pgsql_settings.host,
                port=self.pgsql_settings.port,
                database=self.pgsql_settings.database,
                user=self.pgsql_settings.user,
                password=self.pgsql_settings.password,
            )
