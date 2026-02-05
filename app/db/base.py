import psycopg
import os

DATABASE_URL = os.getenv("DATABASE_URL")
_conn = None

def get_connection():
    global _conn
    if _conn is None:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is not set")
        _conn = psycopg.connect(DATABASE_URL)
        _conn.autocommit = True
    return _conn


def getCursor():
    return get_connection().cursor()
