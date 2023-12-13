import datetime
import logging
import signal
from typing import Any

from common.settings import WorkerSettings
from common.worker import Bootstrap, Worker
from worker_extract.container import WorkerExtractContainer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkerExtract(Worker):
    def __init__(self, settings: WorkerSettings):
        super().__init__(settings)
        self.terminated = False
        self.interrupted = False
        self.container = WorkerExtractContainer(self.settings)
        self.num_files = settings.NUM_FILES

    async def run(self) -> None:
        signal.signal(signal.SIGTERM, self.signal_term)
        signal.signal(signal.SIGINT, self.signal_int)
        await self.container.database.initialize()

        num_files = self.num_files
        logger.info(f"Extracting Number of files: {num_files}")
        try:
            start_time = datetime.datetime.now()
            self.container.extract_command.execute(
                malicious=False, num_files=num_files // 2
            )
            self.container.extract_command.execute(
                malicious=True, num_files=num_files // 2
            )
            end_time = datetime.datetime.now()
            logger.info(f"Time taken: {end_time - start_time}")

        finally:
            self.container.close()

    def signal_term(self, *args: Any) -> None:
        logger.info("Received signal terminate")
        self.terminated = True

    def signal_int(self, *args: Any) -> None:
        logger.info("Received signal interrupted")
        self.interrupted = True


def main() -> None:
    settings = WorkerSettings()
    Bootstrap({"extract": WorkerExtract}, settings).run()


if __name__ == "__main__":
    main()
