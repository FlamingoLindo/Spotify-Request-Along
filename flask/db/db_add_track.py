import psycopg2

import os

DB = os.getenv("POSTGRES_DB")
USER = os.getenv("POSTGRES_USER")
PASS = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST")
PORT = os.getenv("POSTGRES_PORT")


def track_exists_in_db(uri: str) -> bool:
    """Check if a track already exists in the database.
    
    Args:
        uri (str): Spotify track URI
        
    Returns:
        bool: True if track exists, False otherwise
    """
    try:
        conn = psycopg2.connect(database=DB,
                                user=USER,
                                password=PASS,
                                host=HOST, port=PORT)

        cur = conn.cursor()

        cur.execute("SELECT uri FROM tracks WHERE uri = %s;", (uri,))
        existing_track = cur.fetchone()

        cur.close()
        conn.close()
        
        return existing_track is not None
    except Exception as e:
        print("Error checking track in DB: ", e)
        return False


def db_add_track(uri: str, track_name: str) -> bool:
    """Add a track to the database if it doesn't already exist.
    
    Args:
        uri (str): Spotify track URI
        track_name (str): Name of the track
        
    Returns:
        bool: True if track was added, False if it already existed
    """
    try:
        conn = psycopg2.connect(database=DB,
                                user=USER,
                                password=PASS,
                                host=HOST, port=PORT)

        cur = conn.cursor()

        cur.execute("SELECT uri FROM tracks WHERE uri = %s;", (uri,))
        existing_track = cur.fetchone()

        if existing_track:
            cur.close()
            conn.close()
            return False

        cur.execute(
            "INSERT INTO tracks (uri, name) VALUES (%s, %s) ON CONFLICT (uri) DO NOTHING;",
            (uri, track_name)
        )

        conn.commit()

        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("Error adding track in DB: ", e)
        return False
