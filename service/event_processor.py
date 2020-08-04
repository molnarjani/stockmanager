from connection import connection
from logger import logger


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
    else:
        new_amount = amount + int(event["value"])
        query = "UPDATE items SET amount = %s WHERE store_id = %s and item_id = %s"
        cursor.execute(query, (new_amount, event["store_number"], event["item_number"]))


def decrease_stock_amount(cursor, event):
    """ Decreases the stock amount of an Item
        If the Store does not already exist, TODO
        If it exists, it decreases its amount
        If the amount would be less than 0, it retries
    """
    amount = lookup_item_amount(cursor, event)
    if amount is None:
        # TODO: handle not existing item
        return

    new_amount = amount - int(event["value"])
    if new_amount < 0:
        # TODO: resend event to kafka topic N times
        return

    query = "UPDATE items SET amount = %s WHERE store_id = %s and item_id = %s"
    cursor.execute(query, (new_amount, event["store_number"], event["item_number"]))
    logger.info(amount)


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
