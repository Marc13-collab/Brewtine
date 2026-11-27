from datetime import date, datetime, timezone

from app.clock import today_manila


def test_just_after_manila_midnight_is_next_day():
    assert today_manila(datetime(2026, 11, 26, 16, 30, tzinfo=timezone.utc)) == date(2026, 11, 27)


def test_before_manila_midnight_is_same_day():
    assert today_manila(datetime(2026, 11, 26, 15, 30, tzinfo=timezone.utc)) == date(2026, 11, 26)
