import os

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL", "localhost:9092")
KAFKA_EVENTS_TOPIC = os.environ.get("KAFKA_EVENTS_TOPIC")
KAFKA_ERRORS_TOPIC = os.environ.get("KAFKA_ERRORS_TOPIC")

if KAFKA_EVENTS_TOPIC is None or KAFKA_ERRORS_TOPIC is None or KAFKA_BROKER_URL is None:
    raise ValueError(
        "Please set KAFKA_EVENTS_TOPIC and KAFKA_ERRORS_TOPIC and KAFKA_BROKER_URL environment variables!"
    )
