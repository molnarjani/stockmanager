from connection import connection
from helpers import create_tables, logger

if __name__ == '__main__':
    create_tables(connection)