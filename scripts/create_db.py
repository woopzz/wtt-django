import os
import psycopg
from psycopg import sql

config = {
    'user': os.environ['POSTGRES_USER'],
    'password': os.environ['POSTGRES_PASSWORD'],
    'host': os.environ['POSTGRES_HOST'],
    'port': os.environ['POSTGRES_PORT'],
    'autocommit': True,
}
with psycopg.connect(**config) as conn:
    with conn.cursor() as curs:
        dbname = os.environ['POSTGRES_DATABASE_NAME']
        query = sql.SQL('CREATE DATABASE {}').format(sql.Identifier(dbname))
        curs.execute(query)
