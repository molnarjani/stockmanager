import json

from kafka import KafkaConsumer
from consts import (
    KAFKA_BROKER_URL, KAFKA_EVENTS_TOPIC, KAFKA_ERRORS_TOPIC
)

consumer = KafkaConsumer(
    KAFKA_EVENTS_TOPIC,
    bootstrap_servers=KAFKA_BROKER_URL,
    value_deserializer=json.loads,
)