"""
SQLite database for tracking founders, emails, and daily stats.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from config import DB_PATH

def get_db() -> sqlite3.Connection:
    """Get database connection and ensure tables exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("""
        CREATE TABLE IF NOT EXISTS founders (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            company TEXT,
            company_url TEXT,
            batch TEXT,
            stage TEXT,
            industries TEXT,
            yc_url TEXT,
            status TEXT DEFAULT 'new',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_contacted TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY,
            founder_id INTEGER,
            template_key TEXT,
            subject TEXT,
            body TEXT,
            observation TEXT,
            status TEXT DEFAULT 'draft',
            sent_at TEXT,
            replied_at TEXT,
            FOREIGN KEY (founder_id) REFERENCES founders(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_stats (
            date TEXT PRIMARY KEY,
            emails_sent INTEGER DEFAULT 0,
            emails_opened INTEGER DEFAULT 0,
            replies INTEGER DEFAULT 0,
            companies_fetched INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    return conn

def add_founder(conn: sqlite3.Connection, **kwargs) -> int:
    """Add a founder to the database. Returns the founder ID."""
    # Check if already exists
    existing = conn.execute(
        "SELECT id FROM founders WHERE email = ? OR (name = ? AND company = ?)",
        (kwargs.get("email"), kwargs.get("name"), kwargs.get("company"))
    ).fetchone()

    if existing:
        return existing["id"]

    cursor = conn.execute("""
        INSERT INTO founders (name, email, company, company_url, batch, stage, industries, yc_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        kwargs.get("name"),
        kwargs.get("email"),
        kwargs.get("company"),
        kwargs.get("company_url"),
        kwargs.get("batch"),
        kwargs.get("stage"),
        kwargs.get("industries", ""),
        kwargs.get("yc_url"),
    ))
    conn.commit()
    return cursor.lastrowid

def add_email(conn: sqlite3.Connection, **kwargs) -> int:
    """Add a drafted email. Returns the email ID."""
    cursor = conn.execute("""
        INSERT INTO emails (founder_id, template_key, subject, body, observation, status)
        VALUES (?, ?, ?, ?, ?, 'draft')
    """, (
        kwargs.get("founder_id"),
        kwargs.get("template_key"),
        kwargs.get("subject"),
        kwargs.get("body"),
        kwargs.get("observation"),
    ))
    conn.commit()
    return cursor.lastrowid

def mark_sent(conn: sqlite3.Connection, email_id: int):
    """Mark an email as sent."""
    conn.execute(
        "UPDATE emails SET status = 'sent', sent_at = ? WHERE id = ?",
        (datetime.now().isoformat(), email_id)
    )
    conn.commit()

def mark_contacted(conn: sqlite3.Connection, founder_id: int):
    """Mark a founder as contacted."""
    conn.execute(
        "UPDATE founders SET status = 'contacted', last_contacted = ? WHERE id = ?",
        (datetime.now().isoformat(), founder_id)
    )
    conn.commit()

def get_today_stats(conn: sqlite3.Connection) -> dict:
    """Get today's sending stats."""
    today = datetime.now().strftime("%Y-%m-%d")
    row = conn.execute("SELECT * FROM daily_stats WHERE date = ?", (today,)).fetchone()
    if row:
        return dict(row)
    return {"date": today, "emails_sent": 0, "emails_opened": 0, "replies": 0, "companies_fetched": 0}

def increment_sent(conn: sqlite3.Connection):
    """Increment today's sent count."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn.execute("""
        INSERT INTO daily_stats (date, emails_sent) VALUES (?, 1)
        ON CONFLICT(date) DO UPDATE SET emails_sent = emails_sent + 1
    """, (today,))
    conn.commit()

def can_send_more(conn: sqlite3.Connection, daily_limit: int) -> bool:
    """Check if we're under the daily limit."""
    stats = get_today_stats(conn)
    return stats["emails_sent"] < daily_limit

def get_uncontacted_founders(conn: sqlite3.Connection, limit: int = 50) -> list[dict]:
    """Get founders we haven't contacted yet."""
    rows = conn.execute("""
        SELECT * FROM founders
        WHERE status = 'new' AND email IS NOT NULL
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    return [dict(r) for r in rows]

def get_draft_emails(conn: sqlite3.Connection, limit: int = 25) -> list[dict]:
    """Get emails ready to send."""
    rows = conn.execute("""
        SELECT e.*, f.name as founder_name, f.email as founder_email, f.company
        FROM emails e
        JOIN founders f ON e.founder_id = f.id
        WHERE e.status = 'draft'
        LIMIT ?
    """, (limit,)).fetchall()
    return [dict(r) for r in rows]

def get_stats_summary(conn: sqlite3.Connection) -> dict:
    """Get overall stats."""
    total_sent = conn.execute("SELECT COUNT(*) as c FROM emails WHERE status = 'sent'").fetchone()["c"]
    total_replies = conn.execute("SELECT COUNT(*) as c FROM emails WHERE replied_at IS NOT NULL").fetchone()["c"]
    total_founders = conn.execute("SELECT COUNT(*) as c FROM founders").fetchone()["c"]
    total_contacted = conn.execute("SELECT COUNT(*) as c FROM founders WHERE status = 'contacted'").fetchone()["c"]

    return {
        "total_founders": total_founders,
        "total_contacted": total_contacted,
        "total_sent": total_sent,
        "total_replies": total_replies,
        "reply_rate": (total_replies / total_sent * 100) if total_sent > 0 else 0,
    }
