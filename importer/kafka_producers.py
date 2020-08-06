import os
import json
import time
import traceback
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from logger import logger
from consts import (
    KAFKA_CONNECTION_ERROR_MESSAGE_TEMPLATE,
    KAFKA_BROKER_URL,
    KAFKA_EVENTS_TOPIC,
    KAFKA_ERRORS_TOPIC,
)

schema = {
    "type": "object",
    "properties": {
        "transaction_id": {"$ref": "#/definitions/non-empty-string"},
        "event_type": {"type": "string", "enum": ["incoming", "sale"]},
        "date": {"$ref": "#/definitions/non-empty-string"},
        "store_number": {"$ref": "#/definitions/non-empty-string"},
        "item_number": {"$ref": "#/definitions/non-empty-string"},
        "value": {"$ref": "#/definitions/non-empty-string"},
    },
    "required": [
        "transaction_id",
        "event_type",
        "date",
        "store_number",
        "item_number",
        "value",
    ],
    "definitions": {"non-empty-string": {"type": "string", "minLength": 1},},
}


def serialize(value):
    """ Validates event agains schema, then serializes to bytestring """
    validate(value, schema)
    return json.dumps(value).encode("utf-8")


try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL, value_serializer=serialize,
    )

    # Skip schema validation
    error_producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )
except NoBrokersAvailable:
    raise ConnectionError(
        KAFKA_CONNECTION_ERROR_MESSAGE_TEMPLATE.format(broker_url=KAFKA_BROKER_URL)
    )


def send_error(payload):
    error_producer.send(KAFKA_ERRORS_TOPIC, value=payload)


def send_event(payload):
    try:
        producer.send(KAFKA_EVENTS_TOPIC, value=payload)
    except ValidationError as e:
        exc = traceback.format_exc()
        logger.error(exc)
        payload["error"] = exc
        send_error(payload)
