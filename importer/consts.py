KAFKA_CONNECTION_ERROR_MESSAGE_TEMPLATE = """
    Could not connect to Kafka broker at {broker_url}!
    Make sure Kafka is running or start it with:
    docker-compose -f docker-compose.kafka.yml up
"""