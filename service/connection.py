""" Sets up connection to Postgres database """
import os
import psycopg2

connection = None
hostname = os.environ.get("POSTGRES_HOSTNAME", "localhost:5432")
user = os.environ.get("POSTGRES_USER")
password = os.environ.get("POSTGRES_PASSWORD")
db_name = os.environ.get("POSTGRES_DB")

if user is None or password is None or db_name is None:
    raise ValueError(
        "Please set POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB environmnt variables!"
    )

connection = psycopg2.connect(
    dbname=db_name, user=user, host=hostname, password=password
)
connection.autocommit = False
