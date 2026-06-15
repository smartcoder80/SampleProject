import os
from psycopg2 import pool

# Supabase PostgreSQL connection — override any value via environment variables
DB_CONFIG = {
    "host":     os.environ.get("DB_HOST",     "db.pwxppfatzndrcvlckcvm.supabase.co"),
    "port":     int(os.environ.get("DB_PORT", 5432)),
    "dbname":   os.environ.get("DB_NAME",     "postgres"),
    "user":     os.environ.get("DB_USER",     "postgres"),
    "password": os.environ.get("DB_PASSWORD", "suntim@2026"),
    "sslmode":  "require",
}

SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key-in-production")

# Thread-safe connection pool (min 1, max 10 connections)
connection_pool = pool.ThreadedConnectionPool(1, 10, **DB_CONFIG)


def get_db():
    """Borrow a connection from the pool."""
    return connection_pool.getconn()


def release_db(conn):
    """Return a connection to the pool."""
    connection_pool.putconn(conn)
