import os
import time
from kafka import KafkaProducer

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL", 'localhost:9092')

producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER_URL)