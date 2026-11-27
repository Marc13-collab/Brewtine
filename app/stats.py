"""Streak and weekly-progress rules. Pure functions: no database, no clock."""
from datetime import timedelta


def compute_streak(check_dates, today):
    """Consecutive checked days ending today, or ending yesterday if today is not checked yet."""
    day = today if today in check_dates else today - timedelta(days=1)
    streak = 0
    while day in check_dates:
        streak += 1
        day -= timedelta(days=1)
    return streak


def week_bounds(today):
    """(Monday, Sunday) of the calendar week containing today."""
    monday = today - timedelta(days=today.weekday())
    return monday, monday + timedelta(days=6)


def week_progress(check_dates, today, weekly_target):
    """Check-ins this week against the target. Percent is whole-number, floored, capped at 100."""
    monday, sunday = week_bounds(today)
    count = sum(1 for day in check_dates if monday <= day <= sunday)
    return {
        'count': count,
        'target': weekly_target,
        'percent': min(100, count * 100 // weekly_target),
    }


def week_strip(check_dates, today):
    """Seven states, Monday to Sunday: 'checked', 'missed' (an earlier day, unchecked) or 'upcoming'.

    Today unchecked counts as 'upcoming': the day is not over yet, so it cannot be missed.
    """
    monday, _ = week_bounds(today)
    strip = []
    for offset in range(7):
        day = monday + timedelta(days=offset)
        if day in check_dates:
            strip.append('checked')
        elif day < today:
            strip.append('missed')
        else:
            strip.append('upcoming')
    return strip
