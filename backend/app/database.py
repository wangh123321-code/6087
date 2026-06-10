import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "running.db")


def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS run_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            distance REAL NOT NULL,
            duration INTEGER NOT NULL,
            avg_pace REAL NOT NULL,
            avg_heart_rate INTEGER,
            location TEXT DEFAULT '',
            weather TEXT DEFAULT '',
            feeling TEXT DEFAULT '',
            training_type TEXT DEFAULT '',
            gpx_data TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_run_records_date ON run_records(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_run_records_distance ON run_records(distance)")

    cursor.execute("PRAGMA table_info(run_records)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'training_type' not in columns:
        cursor.execute("ALTER TABLE run_records ADD COLUMN training_type TEXT DEFAULT ''")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL UNIQUE,
            target_distance REAL NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()
