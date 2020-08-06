from logger import logger
from collections import defaultdict

from connection import connection
from kafka_producers import send_event, send_error
from consts import KAFKA_EVENT_RETRIES

retry_log = defaultdict(int)


def add_to_event_journal(cursor, event):
    """ Logs transaction event to Transaction journal """
    query = """
    INSERT INTO transactions (transaction_id, event, timestamp, store_number, item_number, amount)
    VALUES(%s,%s,%s,%s,%s,%s)
    ON CONFLICT (transaction_id) DO NOTHING;
    """
    cursor.execute(query, (list(event.values())))


def is_already_processed(cursor, event):
    """ Returns if the the transaction event was already processed """
    query = "select transaction_id from transactions where transaction_id = %s"
    cursor.execute(query, (event["transaction_id"],))
    result = cursor.fetchone()
    return result is not None


def lookup_item_amount(cursor, event):
    """ Looks up current amount for an item
        Returns the amount or None
    """
    query = "SELECT amount FROM items WHERE store_id = %s and item_id = %s"
    cursor.execute(query, (event["store_number"], event["item_number"]))
    results = cursor.fetchone()
    if results is not None:
        return results[0]

    return


def increase_stock_amount(cursor, event):
    """ Increases the stock amount of an Item
        If the Store does not already exist, it creates it with the event value as amount
        If it exists, it increases its amount
    """
    # Add store if it did not exist before
    query = """
        INSERT INTO stores (id)
        VALUES(%s)
        ON CONFLICT (id) DO NOTHING;
    """
    cursor.execute(query, (event["store_number"],))

    amount = lookup_item_amount(cursor, event)

    # Add to store or increase amount
    if amount is None:
        query = """
        INSERT INTO items (item_id, store_id, amount)
        VALUES(%s, %s, %s)
        """
        cursor.execute(
            query, (event["item_number"], event["store_number"], event["value"])
        )
        logger.info(
            "created item: {}-{}, current amount: {}".format(
                event["store_number"], event["item_number"], amount
            )
        )
    else:
        new_amount = amount + int(event["value"])
        query = "UPDATE items SET amount = %s WHERE store_id = %s and item_id = %s"
        cursor.execute(query, (new_amount, event["store_number"], event["item_number"]))
        logger.info(
            "increased item: {}-{}, current amount: {}".format(
                event["store_number"], event["item_number"], new_amount
            )
        )


def retry_event(event, reason=None):
    """ Retries the event KAFKA_EVENT_RETRIES times
        In case it arrived too early, as we cant know the order of transactions
        We just send it back to the Kafka topic in hopes the next time we read it
        
        Currently it does not wait before retrying, depending on business needs,
        it might be worthy to add a delay before re-reading

        If the events are retried KAFKA_EVENT_RETRIES times already
        an error is raised to KAFKA_ERRORS_TOPIC
    """
    transaction_id = event["transaction_id"]
    if retry_log[transaction_id] >= KAFKA_EVENT_RETRIES:
        event["error"] = reason
        send_error(event)
        logger.error("Retries exceeded! event: {}".format(event))
        return

    send_event(event)
    retry_log[transaction_id] += 1
    logger.info("Resent event: {}".format(event))


def decrease_stock_amount(cursor, event):
    """ Decreases the stock amount of an Item
        If the Store does not already exist, TODO
        If it exists, it decreases its amount
        If the amount would be less than 0, it retries
    """
    amount = lookup_item_amount(cursor, event)
    if amount is None:
        retry_event(
            event,
            reason="{}-{} does not exist!".format(
                event["store_number"], event["item_number"]
            ),
        )
        return

    new_amount = amount - int(event["value"])
    if new_amount < 0:
        retry_event(
            event,
            reason="{}-{} stock amount would be less than 0: {}!".format(
                event["store_number"], event["item_number"], new_amount
            ),
        )
        return

    query = "UPDATE items SET amount = %s WHERE store_id = %s and item_id = %s"
    cursor.execute(query, (new_amount, event["store_number"], event["item_number"]))
    logger.info(
        "decreased item: {}-{}, current amount: {}".format(
            event["store_number"], event["item_number"], new_amount
        )
    )


def process_atomic_transaction_event(event):
    """ Processes an transaction event from KafkaConsumer
        Transaction events are processed atomically

        If Transaction was already prooessed, it skips
        otherwise tries to process <event_type>

        event_types:
            - incoming: increase stock amount in store       
            - sale:     decrese stock amount in store       
    """
    with connection:
        with connection.cursor() as cursor:
            if not is_already_processed(cursor, event):
                if event["event_type"] == "incoming":
                    increase_stock_amount(cursor, event)
                elif event["event_type"] == "sale":
                    decrease_stock_amount(cursor, event)
