import logging
from contextlib import contextmanager
from connection import connection


logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S') 
logger = logging.getLogger()


@contextmanager
def transaction(connection):
    cursor = connection.cursor()
    try:
        yield cursor
    except:
        connection.rollback()
        raise
    else:
        connection.commit()
    finally:
        connection.close()


def create_tables(connection):
    with transaction(connection):
        cursor = connection.cursor()
        cursor.execute(
            """
                DO $$ BEGIN
                    CREATE TYPE event_type AS ENUM ('incoming', 'sale');
                    CREATE TABLE IF NOT EXISTS transactions (
                        transaction_id uuid PRIMARY KEY,
                        event event_type,
                        timestamp timestamptz,
                        store_number int,
                        item_number int,
                        value int
                    );
                EXCEPTION
                    -- Types cannot be recreated easily
                    -- they dont have "IF NOT EXISTS" modifier either
                    -- thus catching this specific exception as per:
                    -- https://www.thetopsites.net/article/50011731.shtml

                    WHEN duplicate_object THEN null;
                END $$;
            """
        )
        cursor.execute(
            """
                SELECT *
                FROM pg_catalog.pg_tables
                WHERE schemaname != 'pg_catalog' AND 
                    schemaname != 'information_schema';
            """
        )
        tables = cursor.fetchone()
        logger.info(tables)

