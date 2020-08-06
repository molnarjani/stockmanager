import os
import json
import time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from consts import (
    KAFKA_CONNECTION_ERROR_MESSAGE_TEMPLATE,
    KAFKA_BROKER_URL,
    KAFKA_EVENTS_TOPIC,
    KAFKA_ERRORS_TOPIC,
)

try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )
except NoBrokersAvailable:
    raise ConnectionError(
        KAFKA_CONNECTION_ERROR_MESSAGE_TEMPLATE.format(broker_url=KAFKA_BROKER_URL)
    )


def send_event(payload):
    producer.send(KAFKA_EVENTS_TOPIC, value=payload)


def send_error(payload):
    producer.send(KAFKA_ERRORS_TOPIC, value=payload)
