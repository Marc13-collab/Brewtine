import psycopg


def get_conn(url):
    return psycopg.connect(url, connect_timeout=5)


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
