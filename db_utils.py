import sqlite3
import time
import logging

logger = logging.getLogger(__name__)

# SQLite configuration for better concurrency
sqlite3.connect(":memory:").isolation_level = None

def get_db_connection(db_file, timeout=30, retries=3):
    """
    Get database connection with retry logic and timeout
    
    Args:
        db_file: Database file path
        timeout: Connection timeout in seconds
        retries: Number of retry attempts
    
    Returns:
        sqlite3.Connection
    """
    for attempt in range(retries):
        try:
            conn = sqlite3.connect(db_file, timeout=timeout)
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            return conn
        except sqlite3.OperationalError as e:
            if attempt < retries - 1:
                wait_time = 0.5 * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Database locked, retrying in {wait_time}s... (attempt {attempt + 1}/{retries})")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to connect to database after {retries} attempts: {e}")
                raise

def execute_query(db_file, query, params=None, fetch=False):
    """
    Execute a query with retry logic
    
    Args:
        db_file: Database file path
        query: SQL query string
        params: Query parameters (tuple or list)
        fetch: If True, fetch results; if False, just execute
    
    Returns:
        Query results if fetch=True, else None
    """
    conn = None
    try:
        conn = get_db_connection(db_file)
        c = conn.cursor()
        
        if params:
            c.execute(query, params)
        else:
            c.execute(query)
        
        if fetch:
            return c.fetchall()
        else:
            conn.commit()
            return None
    except Exception as e:
        logger.error(f"Database error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
