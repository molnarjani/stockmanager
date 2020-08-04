""" Application entrypoint """


def process_events(consumer):
    """ Consumes and processes events in KafkaConsumer """
    for message in consumer:
        event = message.value
        try:
            process_atomic_transaction_event(event)
            logger.info("processed event: {}".format(event))
        except Exception:
            logger.exception("could not process event: {}".format(event))


if __name__ == "__main__":
    import traceback
    from connection import connection
    from helpers import create_app_tables
    from logger import logger
    from kafka_consumers import consumer
    from event_processor import process_atomic_transaction_event

    create_app_tables(connection)
    process_events(consumer)
    connection.close()
