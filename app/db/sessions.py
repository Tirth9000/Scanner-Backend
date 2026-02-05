import psycopg
import os

# create db if it doesnt exists
def init_db():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # extract db name from db url
    db_name = DATABASE_URL.rsplit('/', 1)[-1]
    base_url = DATABASE_URL.rsplit('/', 1)[0] + '/postgres'
    
    try:
        conn = psycopg.connect(base_url, autocommit=True)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        
        if not cursor.fetchone():
            # Use SQL composition for safe identifier quoting
            from psycopg import sql
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            print(f"Database '{db_name}' created successfully")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Could not create database: {e}")


# create tables if it doesnt exists
def init_tables():
    from app.db.base import getCursor
    cursor = getCursor()

    # create table if if doesnt exist
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(36) PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    
    cursor.close()
    print("Database initialized successfully")
