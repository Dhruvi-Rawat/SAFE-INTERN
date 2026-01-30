# database/pattern_repository.py
"""
Pattern repository for SAFE-INTERN.

Responsibilities:
- Track how often specific risk patterns appear
- Update occurrence counts for agent-detected patterns
- Provide lightweight analytics support (no scoring logic)

Used by:
- Company agent
- Payment agent
- Behavior agent
- ML agent (optional)

NO risk decisions
NO user-facing logic
"""

from typing import Optional
from database.db_connection import get_db_connection


# ---------- CREATE / UPDATE PATTERN ----------

def record_pattern(pattern_type: str, pattern_key: str) -> None:
    """
    Insert or update a risk pattern occurrence.

    Args:
        pattern_type: company | payment | behavior | ml
        pattern_key: rule name or signal identifier
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if pattern already exists
    cursor.execute(
        """
        SELECT id, occurrences FROM risk_patterns
        WHERE pattern_type = ? AND pattern_key = ?
        """,
        (pattern_type, pattern_key)
    )

    row = cursor.fetchone()

    if row:
        # Update existing pattern
        cursor.execute(
            """
            UPDATE risk_patterns
            SET occurrences = occurrences + 1,
                last_seen = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (row[0],)
        )
    else:
        # Insert new pattern
        cursor.execute(
            """
            INSERT INTO risk_patterns (pattern_type, pattern_key, occurrences)
            VALUES (?, ?, 1)
            """,
            (pattern_type, pattern_key)
        )

    conn.commit()
    conn.close()


# ---------- QUERY HELPERS ----------

def get_pattern_occurrences(pattern_type: str, pattern_key: str) -> int:
    """
    Get total occurrence count for a pattern.

    Args:
        pattern_type: company | payment | behavior | ml
        pattern_key: rule name or signal identifier

    Returns:
        Occurrence count (0 if not found)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT occurrences FROM risk_patterns
        WHERE pattern_type = ? AND pattern_key = ?
        """,
        (pattern_type, pattern_key)
    )

    row = cursor.fetchone()
    conn.close()

    return row[0] if row else 0


def get_top_patterns(limit: int = 10):
    """
    Get most frequently observed patterns.

    Args:
        limit: Number of patterns to return

    Returns:
        List of (pattern_type, pattern_key, occurrences)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT pattern_type, pattern_key, occurrences
        FROM risk_patterns
        ORDER BY occurrences DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows
