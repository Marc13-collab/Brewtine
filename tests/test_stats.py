from datetime import date, timedelta

from app.stats import compute_streak, week_bounds, week_progress, week_strip

T = date(2026, 11, 26)  # a Thursday


def d(n):
    """The date n days before T."""
    return T - timedelta(days=n)


def test_streak_empty():
    assert compute_streak(set(), T) == 0


def test_streak_today_only():
    assert compute_streak({T}, T) == 1


def test_streak_consecutive():
    assert compute_streak({T, d(1), d(2)}, T) == 3


def test_streak_survives_unchecked_today():
    assert compute_streak({d(1), d(2)}, T) == 2


def test_streak_broken_by_gap():
    assert compute_streak({d(2), d(3)}, T) == 0


def test_streak_stops_at_gap():
    assert compute_streak({T, d(1), d(3)}, T) == 2


def test_streak_across_month_end():
    assert compute_streak({date(2026, 11, 30), date(2026, 11, 29)}, date(2026, 12, 1)) == 2


def test_week_bounds_sunday():
    assert week_bounds(date(2026, 11, 29)) == (date(2026, 11, 23), date(2026, 11, 29))


def test_week_bounds_monday():
    assert week_bounds(date(2026, 11, 30)) == (date(2026, 11, 30), date(2026, 12, 6))


def test_progress_partial():
    got = week_progress({date(2026, 11, 23), date(2026, 11, 25), T}, T, 5)
    assert got == {'count': 3, 'target': 5, 'percent': 60}


def test_progress_capped_at_100():
    four = {date(2026, 11, 23), date(2026, 11, 24), date(2026, 11, 25), T}
    assert week_progress(four, T, 3)['percent'] == 100


def test_progress_ignores_last_week():
    assert week_progress({date(2026, 11, 22)}, T, 7)['count'] == 0


def test_progress_floors():
    assert week_progress({T}, T, 7)['percent'] == 14


def test_strip_mixed():
    got = week_strip({date(2026, 11, 23), date(2026, 11, 25), T}, T)
    assert got == ['checked', 'missed', 'checked', 'checked', 'upcoming', 'upcoming', 'upcoming']


def test_strip_today_unchecked_is_upcoming():
    got = week_strip({date(2026, 11, 23)}, T)
    assert got == ['checked', 'missed', 'missed', 'upcoming', 'upcoming', 'upcoming', 'upcoming']


def test_strip_on_monday_is_all_upcoming_until_checked():
    monday = date(2026, 11, 30)
    assert week_strip(set(), monday) == ['upcoming'] * 7
    assert week_strip({monday}, monday)[0] == 'checked'


def test_strip_ignores_last_week():
    assert week_strip({date(2026, 11, 22)}, T)[0] == 'missed'
