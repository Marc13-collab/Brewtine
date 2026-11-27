from pathlib import Path

import psycopg
from psycopg.rows import dict_row

SCHEMA_PATH = Path(__file__).resolve().parent.parent / 'schema.sql'


def get_conn(url):
    """Open a connection. Use it as `with get_conn(url) as conn:` so it commits and closes."""
    return psycopg.connect(url, connect_timeout=5, row_factory=dict_row)


def init_schema(conn):
    """Create the tables if they do not exist. Safe to run more than once."""
    conn.execute(SCHEMA_PATH.read_text())


def _habit_dict(row):
    habit = {
        'id': row['id'],
        'name': row['name'],
        'weekly_target': row['weekly_target'],
        'created_at': row['created_at'].isoformat(),
    }
    if 'checked_today' in row:
        habit['checked_today'] = row['checked_today']
    return habit


def list_habits(conn, today):
    rows = conn.execute(
        'SELECT h.id, h.name, h.weekly_target, h.created_at, '
        '(c.id IS NOT NULL) AS checked_today '
        'FROM habits h '
        'LEFT JOIN check_ins c ON c.habit_id = h.id AND c.check_date = %s '
        'ORDER BY h.id',
        (today,),
    ).fetchall()
    return [_habit_dict(r) for r in rows]


def insert_habit(conn, name, weekly_target):
    row = conn.execute(
        'INSERT INTO habits (name, weekly_target) VALUES (%s, %s) '
        'RETURNING id, name, weekly_target, created_at',
        (name, weekly_target),
    ).fetchone()
    return _habit_dict(row)


def toggle_check_in(conn, habit_id, day):
    """Flip the check-in for that day. Returns the new state, or None if the habit is missing."""
    if conn.execute('SELECT 1 FROM habits WHERE id = %s', (habit_id,)).fetchone() is None:
        return None
    removed = conn.execute(
        'DELETE FROM check_ins WHERE habit_id = %s AND check_date = %s RETURNING id',
        (habit_id, day),
    ).fetchone()
    if removed:
        return False
    conn.execute(
        'INSERT INTO check_ins (habit_id, check_date) VALUES (%s, %s) ON CONFLICT DO NOTHING',
        (habit_id, day),
    )
    return True


def delete_habit(conn, habit_id):
    """Delete a habit (its check-ins go with it). Returns False if it did not exist."""
    row = conn.execute('DELETE FROM habits WHERE id = %s RETURNING id', (habit_id,)).fetchone()
    return row is not None


def check_dates_by_habit(conn):
    """Map each habit id to the set of dates it was checked."""
    dates = {}
    for row in conn.execute('SELECT habit_id, check_date FROM check_ins').fetchall():
        dates.setdefault(row['habit_id'], set()).add(row['check_date'])
    return dates
