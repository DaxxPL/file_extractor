import asyncio
import logging
import signal
from typing import Any

from common.settings import WorkerSettings
from common.worker import Bootstrap, Worker
from worker_sync.container import SyncWorkerContainer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SyncWorker(Worker):
    def __init__(self, settings: WorkerSettings):
        super().__init__(settings)
        self.terminated = False
        self.interrupted = False
        self.container = SyncWorkerContainer(self.settings)

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
    settings = WorkerSettings()
    Bootstrap({"sync": SyncWorker}, settings).run()


if __name__ == "__main__":
    main()
