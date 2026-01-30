# database/company_repository.py
"""
Company repository for SAFE-INTERN.

Responsibilities:
- Store lightweight statistics about companies/domains encountered
- Track how often a company/domain appears in analyses
- Record high-level signals (no verdicts, no scoring)

Used for:
- Historical context
- Pattern frequency (NOT ground truth)

NO legitimacy decisions
NO risk scoring
NO user-facing logic
"""

from typing import Optional, Dict, Any
from database.db_connection import get_db_connection


# ---------- CREATE / UPDATE COMPANY ----------

def record_company(
    domain: str,
    uses_free_email: bool = False,
    website_reachable: bool = False
) -> None:
    """
    Insert or update company/domain statistics.

    Args:
        domain: Company website or email domain
        uses_free_email: Whether a free email domain was detected
        website_reachable: Whether website was reachable at analysis time
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id FROM company_risk_stats
        WHERE domain = ?
        """,
        (domain,)
    )

    row = cursor.fetchone()

    if row:
        # Update existing record
        cursor.execute(
            """
            UPDATE company_risk_stats
            SET 
                total_checks = total_checks + 1,
                free_email_hits = free_email_hits + ?,
                unreachable_hits = unreachable_hits + ?,
                last_seen = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                1 if uses_free_email else 0,
                0 if website_reachable else 1,
                row[0]
            )
        )
    else:
        # Insert new company record
        cursor.execute(
            """
            INSERT INTO company_risk_stats (
                domain,
                total_checks,
                free_email_hits,
                unreachable_hits
            )
            VALUES (?, 1, ?, ?)
            """,
            (
                domain,
                1 if uses_free_email else 0,
                0 if website_reachable else 1
            )
        )

    conn.commit()
    conn.close()


# ---------- QUERY HELPERS ----------

def get_company_stats(domain: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve historical stats for a company/domain.

    Args:
        domain: Company website or email domain

    Returns:
        Dictionary of stats or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            domain,
            total_checks,
            free_email_hits,
            unreachable_hits,
            first_seen,
            last_seen
        FROM company_risk_stats
        WHERE domain = ?
        """,
        (domain,)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "domain": row[0],
        "total_checks": row[1],
        "free_email_hits": row[2],
        "unreachable_hits": row[3],
        "first_seen": row[4],
        "last_seen": row[5]
    }
