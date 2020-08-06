import csv
import time
import logging
from pathlib import Path

from watchdog.observers import Observer
from helpers import LoggedRegexMatchingEventHandler
from kafka_producers import send_event
from logger import logger


def process_csv(file_path):
    f = open(file_path)
    reader = csv.DictReader(f)
    for row in reader:
        logger.info(row)
        send_event(row)


if __name__ == "__main__":
    cwd = Path.cwd()
    input_path = cwd / "input"

    csv_handler = LoggedRegexMatchingEventHandler(logger=logger, regexes=[r".*.csv"])
    csv_handler.process = process_csv

    observer = Observer()
    observer.schedule(csv_handler, input_path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
