from datetime import datetime, timezone
from zoneinfo import ZoneInfo

MANILA = ZoneInfo('Asia/Manila')


def today_manila(now=None):
    """Today's date in Manila. `now` must be timezone-aware; it exists so tests can fix the time."""
    now = now or datetime.now(timezone.utc)
    return now.astimezone(MANILA).date()
