import psycopg2
import os
import sys

DB = os.getenv("POSTGRES_DB")
USER = os.getenv("POSTGRES_USER")
PASS = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST")
PORT = os.getenv("POSTGRES_PORT")


def get_db_connection():
    """Get a database connection.
    
    Returns:
        psycopg2.connection: Database connection
    """
    try:
        conn = psycopg2.connect(
            database=DB,
            user=USER,
            password=PASS,
            host=HOST,
            port=PORT
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}", file=sys.stderr)
        raise


def connect_to_db():
    """Initialize database and create tables if they don't exist."""
    conn = None
    try:
        print("Initializing database connection...", flush=True)
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if table already exists to avoid type conflicts
        cur.execute(
            """SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'tracks'
            );"""
        )
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            # Create tracks table
            cur.execute(
                '''CREATE TABLE IF NOT EXISTS tracks (
                    id SERIAL PRIMARY KEY,
                    uri VARCHAR(350) UNIQUE NOT NULL,
                    name VARCHAR(350) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );'''
            )
            conn.commit()
            print("Database table 'tracks' created successfully", flush=True)
        else:
            print("Database table 'tracks' already exists", flush=True)

        cur.close()
    except Exception as e:
        print(f"Error initializing database: {e}", file=sys.stderr, flush=True)
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
