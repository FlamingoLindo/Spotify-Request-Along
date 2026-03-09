import psycopg2

import os

DB = os.getenv("POSTGRES_DB")
USER = os.getenv("POSTGRES_USER")
PASS = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST")
PORT = os.getenv("POSTGRES_PORT")


def connect_to_db():
    try:
        conn = psycopg2.connect(database=DB,
                                user=USER,
                                password=PASS,
                                host=HOST, port=PORT)

        cur = conn.cursor()

        cur.execute(
            '''CREATE TABLE IF NOT EXISTS tracks (id serial \
            PRIMARY KEY, uri varchar(350) UNIQUE, name varchar(350));''')

        conn.commit()

        cur.close()
        conn.close()
    except Exception as e:
        print("Error connecting to the DB: ", e)
