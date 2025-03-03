import psycopg2
from src.config import Config

def get_db_connection():
    """Create and return a new database connection."""
    return psycopg2.connect(Config.DATABASE_URL) 