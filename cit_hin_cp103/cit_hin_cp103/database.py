"""SQLite persistence layer for CIT HUB."""
import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).parent / "data" / "cit_hub.db"

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextmanager
def get_connection():
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def initialize_database():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS equipment (
            asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_code TEXT NOT NULL UNIQUE COLLATE NOCASE,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            condition TEXT NOT NULL DEFAULT 'Good',
            status TEXT NOT NULL DEFAULT 'Available'
                CHECK(status IN ('Available','Borrowed','Under Maintenance','Inactive'))
        );
        CREATE TABLE IF NOT EXISTS borrowers (
            borrower_id INTEGER PRIMARY KEY AUTOINCREMENT,
            borrower_code TEXT NOT NULL UNIQUE COLLATE NOCASE,
            display_name TEXT NOT NULL,
            department_or_program TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1))
        );
        CREATE TABLE IF NOT EXISTS loans (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER NOT NULL REFERENCES equipment(asset_id),
            borrower_id INTEGER NOT NULL REFERENCES borrowers(borrower_id),
            borrowed_on TEXT NOT NULL,
            due_on TEXT NOT NULL,
            returned_on TEXT,
            status TEXT NOT NULL DEFAULT 'Active'
                CHECK(status IN ('Active','Returned'))
        );
        CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(status);
        CREATE INDEX IF NOT EXISTS idx_equipment_code ON equipment(asset_code);
        """)
