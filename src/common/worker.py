import argparse
import asyncio
import logging
from typing import Optional

from pydantic_settings import BaseSettings


class Worker:
    def __init__(self, settings: BaseSettings):
        self.settings = settings

    async def run(self) -> None:
        raise NotImplementedError


class Bootstrap:
    tasks: Optional[dict[str, type[Worker]]]

    def __init__(self, tasks: dict[str, type[Worker]], settings: BaseSettings):
        self.settings = settings
        self.parser = argparse.ArgumentParser()

        if len(tasks) > 1:
            self.tasks = tasks
            self.parser.add_argument("command", choices=list(tasks.keys()))
        else:
            self.tasks = None
            self.application = tasks.popitem()[1]

        self.parser.add_argument(
            "--log", default="INFO", type=str, dest="log", help="log level"
        )

    def run(self) -> None:
        cmd_args = self.parser.parse_args()

        if cmd_args:
            logging.basicConfig(level=cmd_args.log)
            loop = asyncio.get_event_loop()

            application = (
                self.tasks.get(cmd_args.command) if self.tasks else self.application
            )
            loop.run_until_complete(application(self.settings).run())  # type: ignore

        else:
            self.parser.print_usage()
