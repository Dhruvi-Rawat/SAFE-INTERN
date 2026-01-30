# database/db_init.py
"""
Database initialization for SAFE-INTERN.

Responsibilities:
- Create required tables if they do not exist
- Define schema for pattern tracking, company stats, and metadata
- Run once at application startup

NO application logic
NO data insertion (except defaults)
"""

from database.db_connection import get_db_connection


def init_database() -> None:
    """
    Initialize all database tables.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # ---------- RISK PATTERN TABLE ----------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS risk_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern_type TEXT NOT NULL,          -- company / payment / behavior / ml
        pattern_key TEXT NOT NULL,           -- rule or signal name
        occurrences INTEGER DEFAULT 0,
        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ---------- COMPANY RISK STATS ----------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS company_risk_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT UNIQUE,
        total_checks INTEGER DEFAULT 0,
        high_risk_count INTEGER DEFAULT 0,
        last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ---------- SYSTEM METADATA ----------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE,
        value TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()


# ---------- CLI / MANUAL RUN ----------
if __name__ == "__main__":
    init_database()
    print("SAFE-INTERN database initialized successfully.")
