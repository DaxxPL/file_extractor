import asyncio
import logging
import signal
from typing import Any

from common.worker import Bootstrap, Worker
from worker_sync.container import SyncWorkerContainer
from worker_sync.settings import SyncWorkerSettings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SyncWorker(Worker):
    MICROSECONDS = 1_000_000

    def __init__(self, settings: SyncWorkerSettings):
        super().__init__(settings)
        self.terminated = False
        self.interrupted = False
        self.container = SyncWorkerContainer(self.settings)
        self.period_time = settings.RESYNC_INTERVAL

    async def run(self) -> None:
        signal.signal(signal.SIGTERM, self.signal_term)
        signal.signal(signal.SIGINT, self.signal_int)
        await self.container.database.initialize()

        try:
            await asyncio.gather(
                self.container.sync_command.execute("0", malicious=False),
                self.container.sync_command.execute("1", malicious=True),
            )
        finally:
            await self.container.close()

    def signal_term(self, *args: Any) -> None:
        logger.info("Received signal terminate")
        self.terminated = True

    def signal_int(self, *args: Any) -> None:
        logger.info("Received signal interrupted")
        self.interrupted = True


def main() -> None:
    settings = SyncWorkerSettings()
    Bootstrap({"sync": SyncWorker}, settings).run()


if __name__ == "__main__":
    main()
