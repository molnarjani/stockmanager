import os
import json
import time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from consts import KAFKA_CONNECTION_ERROR_MESSAGE_TEMPLATE

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL", 'localhost:9092')

try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda value: json.dumps(value).encode('utf-8'))
except NoBrokersAvailable:
    raise ConnectionError(
        KAFKA_CONNECTION_ERROR_MESSAGE_TEMPLATE.format(broker_url=KAFKA_BROKER_URL)
    )

def send_event(payload):
    producer.send("events", value=payload)

def send_error(payload):
    producer.send("errors", value=payload)