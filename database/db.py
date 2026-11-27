"""SQLite data layer for Spendly.

Raw sqlite3 — no ORM. Every query in this module (and everything that builds on it)
uses parameterised statements; never interpolate values into SQL strings.
"""

import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

# Repo root, resolved from this file rather than the process CWD, so the database
# always lands beside app.py no matter where python is invoked from.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "spendly.db")

# The canonical expense categories. Import this list instead of re-typing the
# values in forms, filters or validation.
CATEGORIES = [
    "Food",
    "Transport",
    "Bills",
    "Health",
    "Entertainment",
    "Shopping",
    "Other",
]


def get_db():
    """Return a SQLite connection with dict-like rows and foreign keys enforced.

    PRAGMA foreign_keys is per-connection in SQLite, so it has to be set here on
    every connection — setting it once at schema creation time does nothing.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the schema if it does not already exist. Safe to call repeatedly."""
    conn = get_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                email         TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at    TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id),
                amount      REAL NOT NULL,
                category    TEXT NOT NULL,
                date        TEXT NOT NULL,
                description TEXT,
                created_at  TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_db():
    """Insert the demo user and sample expenses, once.

    Returns early if any user already exists, so repeated calls (every app start)
    never duplicate data.
    """
    conn = get_db()
    try:
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
            return

        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
        )
        user_id = cursor.lastrowid

        # Days kept low so the dates are valid in any month, including February.
        month = date.today()
        samples = [
            (2, 420.50, "Food", "Weekly grocery run"),
            (4, 85.00, "Transport", "Metro card top-up"),
            (6, 1250.00, "Bills", "Electricity bill"),
            (9, 300.00, "Health", "Pharmacy — vitamins"),
            (12, 199.00, "Entertainment", "Movie tickets"),
            (15, 2499.99, "Shopping", "Running shoes"),
            (18, 150.00, "Other", "Birthday gift"),
            (21, 275.75, "Food", "Dinner with friends"),
        ]

        conn.executemany(
            """
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (user_id, amount, category, month.replace(day=day).isoformat(), description)
                for day, amount, category, description in samples
            ],
        )
        conn.commit()
    finally:
        conn.close()
