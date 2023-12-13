import logging
import os
import time

import requests


logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s", level=logging.INFO
)


def wait_for_spark_master(max_time: int = 60) -> None:
    master_url = os.environ.get("SPARK_MASTER_UI_URL")
    start_time = time.time()
    logging.info(f"Awaiting Spark Master at {master_url}...")

    while True:
        try:
            response = requests.get(master_url)
            if response.status_code == 200:
                logging.info("Connection to Spark Master succeeded!")
                return
        except requests.exceptions.RequestException:
            pass

        if time.time() - start_time >= max_time:
            logging.error("Could not connect to Spark Master within time limit!")
            raise TimeoutError(f"Timeout waiting for Spark Master at {master_url}")

        logging.info("Failed to connect to Spark Master. Retrying...")
        time.sleep(5)


def main() -> None:
    wait_for_spark_master()


if __name__ == "__main__":
    main()
