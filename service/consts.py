import os

KAFKA_CONNECTION_ERROR_MESSAGE_TEMPLATE = """
    Could not connect to Kafka broker at {broker_url}!
    Make sure Kafka is running or start it with:
    docker-compose -f docker-compose.kafka.yml up
"""

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL", "localhost:9092")
KAFKA_EVENTS_TOPIC = os.environ.get("KAFKA_EVENTS_TOPIC")
KAFKA_ERRORS_TOPIC = os.environ.get("KAFKA_ERRORS_TOPIC")
KAFKA_EVENT_RETRIES = int(os.environ.get("KAFKA_EVENT_RETRIES", 3))

if KAFKA_EVENTS_TOPIC is None or KAFKA_ERRORS_TOPIC is None or KAFKA_BROKER_URL is None:
    raise ValueError(
        "Please set KAFKA_EVENTS_TOPIC and KAFKA_ERRORS_TOPIC and KAFKA_BROKER_URL environment variables!"
    )
