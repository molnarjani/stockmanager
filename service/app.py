from connection import connection
from helpers import create_tables, logger
from kafka_consumers import consumer

if __name__ == '__main__':
    create_tables(connection)