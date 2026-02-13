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
    from db.base import getCursor
    cursor = getCursor()

    # create table if if doesnt exist
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(36) PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            _id INT PRIMARY KEY,
            category_id INT NOT NULL,
            category_name TEXT NOT NULL,
            question_text TEXT NOT NULL,
            options JSONB NOT NULL
        );

    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessment_results (
            _id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            summary JSONB NOT NULL,
            category_scores JSONB NOT NULL,
            answers JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT now()
        );
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_assessment_results_user_id
        ON assessment_results(user_id);
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_results (
            user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            scan_id VARCHAR(36) NOT NULL,
            domain TEXT NOT NULL,
            results JSONB NOT NULL,
            updated_at TIMESTAMP DEFAULT now()
        );
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_scan_results_user_id
        ON scan_results(user_id);
    """)
    
    
    cursor.close()
    print("Database initialized successfully")
