from pathlib import Path

import psycopg
from psycopg.rows import dict_row

SCHEMA_PATH = Path(__file__).resolve().parent.parent / 'schema.sql'


def get_conn(url):
    """Open a connection. Use it as `with get_conn(url) as conn:` so it commits and closes."""
    return psycopg.connect(url, connect_timeout=5, row_factory=dict_row)


def ping(url):
    """Return True if the database answers SELECT 1, False on any error."""
    if not url:
        return False
    try:
        with get_conn(url) as conn:
            conn.execute('SELECT 1')
        return True
    except Exception:
        return False


def init_schema(conn):
    """Create the tables if they do not exist. Safe to run more than once."""
    conn.execute(SCHEMA_PATH.read_text())


def _habit_dict(row):
    return {
        'id': row['id'],
        'name': row['name'],
        'weekly_target': row['weekly_target'],
        'created_at': row['created_at'].isoformat(),
    }


def list_habits(conn):
    rows = conn.execute(
        'SELECT id, name, weekly_target, created_at FROM habits ORDER BY id'
    ).fetchall()
    return [_habit_dict(r) for r in rows]


def insert_habit(conn, name, weekly_target):
    row = conn.execute(
        'INSERT INTO habits (name, weekly_target) VALUES (%s, %s) '
        'RETURNING id, name, weekly_target, created_at',
        (name, weekly_target),
    ).fetchone()
    return _habit_dict(row)
