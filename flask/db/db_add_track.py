import os
import sys
from db.db_connect import get_db_connection


def track_exists_in_db(uri: str) -> bool:
    """Check if a track already exists in the database.
    
    Args:
        uri (str): Spotify track URI
        
    Returns:
        bool: True if track exists, False otherwise
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT uri FROM tracks WHERE uri = %s;", (uri,))
        existing_track = cur.fetchone()

        cur.close()
        
        return existing_track is not None
    except Exception as e:
        print(f"Error checking track in DB: {e}", file=sys.stderr)
        return False
    finally:
        if conn:
            conn.close()


def db_add_track(uri: str, track_name: str) -> bool:
    """Add a track to the database if it doesn't already exist.
    
    Args:
        uri (str): Spotify track URI
        track_name (str): Name of the track
        
    Returns:
        bool: True if track was added, False if it already existed
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT uri FROM tracks WHERE uri = %s;", (uri,))
        existing_track = cur.fetchone()

        if existing_track:
            cur.close()
            return False

        cur.execute(
            "INSERT INTO tracks (uri, name) VALUES (%s, %s) ON CONFLICT (uri) DO NOTHING;",
            (uri, track_name)
        )

        conn.commit()
        cur.close()
        
        print(f"Successfully added track to DB: {track_name}")
        return True
    except Exception as e:
        print(f"Error adding track in DB: {e}", file=sys.stderr)
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
