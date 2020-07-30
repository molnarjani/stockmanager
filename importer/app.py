import time
import logging 
from pathlib import Path

from kafka_producers import producer
from watchdog.observers import Observer 
from helpers import LoggedRegexMatchingEventHandler

if __name__ == '__main__':
    cwd = Path.cwd()
    input_path = cwd / 'input'

    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(message)s', 
                        datefmt='%Y-%m-%d %H:%M:%S') 
    logger = logging.getLogger()

    csv_handler = LoggedRegexMatchingEventHandler(logger=logger, regexes=[r'.*.csv'])

    observer = Observer() 
    observer.schedule(csv_handler, input_path, recursive=True) 
    observer.start() 

    try: 
        while True: 
            time.sleep(1) 
    except KeyboardInterrupt: 
        observer.stop() 
    observer.join() 