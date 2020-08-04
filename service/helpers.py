import sys
from contextlib import contextmanager
from psycopg2 import sql

from connection import connection
from logger import logger


def create_app_tables(connection):
    """ Creates tables needed for the application if they don't already exist """
    with connection:
        with connection.cursor() as cursor:
            # Create event_type
            cursor.execute(
                """
                    DO $$ BEGIN
                        CREATE TYPE event_type AS ENUM ('incoming', 'sale');
                    EXCEPTION
                        -- Types cannot be recreated easily
                        -- they dont have "IF NOT EXISTS" modifier either
                        -- thus catching this specific exception as per:
                        -- https://www.thetopsites.net/article/50011731.shtml

                        WHEN duplicate_object THEN null;
                    END $$;
                """
            )
            # Create `transactions` table
            cursor.execute(
                """
                    CREATE TABLE IF NOT EXISTS transactions (
                        transaction_id uuid PRIMARY KEY,
                        event event_type,
                        timestamp timestamptz,
                        store_number int,
                        item_number int,
                        amount int
                    );
                """
            )
            # Create `stores` table
            cursor.execute(
                """
                    CREATE TABLE IF NOT EXISTS stores (
                        id int PRIMARY KEY
                );
                """
            )
            # Create `items` table
            cursor.execute(
                """
                    CREATE TABLE IF NOT EXISTS items (
                        id SERIAL,
                        item_id int,
                        store_id int,
                        amount int,
                        CONSTRAINT fk_store
                            FOREIGN KEY(store_id) 
                                REFERENCES stores(id)
                                ON DELETE CASCADE
                );
                """
            )
            logger.info("App tables created!")
