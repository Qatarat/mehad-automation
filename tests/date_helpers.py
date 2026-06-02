"""
Dynamic date helpers for Mehad QA tests.

All date calculations are relative to today so tests never break
because a hardcoded calendar date has passed.  Import these into any
test file instead of writing literal "2026-06-08" values.
"""
from __future__ import annotations
from datetime import date, datetime, timedelta


# ─── Weekday constants ────────────────────────────────────────────────────────
MON, TUE, WED, THU, FRI, SAT, SUN = 0, 1, 2, 3, 4, 5, 6


def next_weekday(weekday: int, *, min_days_ahead: int = 1) -> date:
    """Return the nearest future date that falls on `weekday`.

    Args:
        weekday:        0 = Monday … 6 = Sunday
        min_days_ahead: how many days from today must the result be at minimum
                        (default 1 = strictly in the future, not today)
    """
    today = date.today()
    days_ahead = (weekday - today.weekday()) % 7
    if days_ahead < min_days_ahead:
        days_ahead += 7
    return today + timedelta(days=days_ahead)


def next_monday(*, weeks_ahead: int = 1) -> date:
    """Next Monday that is at least `weeks_ahead` ISO weeks from today."""
    base = next_weekday(MON, min_days_ahead=1)
    return base + timedelta(weeks=weeks_ahead - 1)


def next_tuesday(*, weeks_ahead: int = 1) -> date:
    base = next_weekday(TUE, min_days_ahead=1)
    return base + timedelta(weeks=weeks_ahead - 1)


def next_wednesday(*, weeks_ahead: int = 1) -> date:
    base = next_weekday(WED, min_days_ahead=1)
    return base + timedelta(weeks=weeks_ahead - 1)


def days_from_now(n: int) -> date:
    """Return date that is exactly *n* days from today (n ≥ 1)."""
    return date.today() + timedelta(days=max(n, 1))


# ─── Formatting helpers ───────────────────────────────────────────────────────

def fmt_input(d: date) -> str:
    """YYYY-MM-DD — suitable for <input type="date"> .fill()."""
    return d.strftime("%Y-%m-%d")


def fmt_display(d: date) -> str:
    """e.g. 'Monday, June 9, 2026' — matches the booking modal summary."""
    return d.strftime("%A, %B %-d, %Y")


def fmt_short(d: date) -> str:
    """e.g. 'Jun 9' — matches calendar cell labels."""
    return d.strftime("%b %-d")


def fmt_day_num(d: date) -> str:
    """Zero-padded day number string, e.g. '09' — matches modal day buttons."""
    return d.strftime("%d")


def fmt_month_year(d: date) -> str:
    """e.g. 'June 2026' — matches calendar month header."""
    return d.strftime("%B %Y")


# ─── Pre-built slot helpers used across test files ────────────────────────────

def availability_slot_monday() -> dict:
    """
    Earliest next Monday that is ≥ 2 days away (gives API time to propagate).
    Returns a dict ready to unpack in availability + booking tests.
    """
    d = next_weekday(MON, min_days_ahead=2)
    return {
        "date":        d,
        "input":       fmt_input(d),
        "display":     fmt_display(d),
        "short":       fmt_short(d),
        "day_num":     fmt_day_num(d),
        "month_year":  fmt_month_year(d),
        "start_time":  "10:00 AM",
        "end_time":    "12:00 PM",
    }


def availability_slot_tuesday() -> dict:
    d = next_weekday(TUE, min_days_ahead=2)
    return {
        "date":        d,
        "input":       fmt_input(d),
        "display":     fmt_display(d),
        "short":       fmt_short(d),
        "day_num":     fmt_day_num(d),
        "month_year":  fmt_month_year(d),
        "start_time":  "2:00 PM",
        "end_time":    "4:00 PM",
    }


def availability_slot_wednesday() -> dict:
    d = next_weekday(WED, min_days_ahead=2)
    return {
        "date":        d,
        "input":       fmt_input(d),
        "display":     fmt_display(d),
        "short":       fmt_short(d),
        "day_num":     fmt_day_num(d),
        "month_year":  fmt_month_year(d),
        "start_time":  "6:00 PM",
        "end_time":    "8:00 PM",
    }


def group_session_date() -> dict:
    """
    Group session is scheduled on the Monday 2 weeks from now so there is
    no collision with the 1-on-1 availability slot.
    """
    d = next_weekday(MON, min_days_ahead=8)   # at least next-next Monday
    return {
        "date":        d,
        "input":       fmt_input(d),
        "display":     fmt_display(d),
        "short":       fmt_short(d),
        "day_num":     fmt_day_num(d),
        "month_year":  fmt_month_year(d),
        "start_time":  "10:00 AM",
        "end_time":    "12:00 PM",
    }


def booking_slot() -> dict:
    """The student books the Monday slot that the teacher opened above."""
    return availability_slot_monday()


# ─── Quick self-test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    s = availability_slot_monday()
    print(f"availability monday  : {s['display']}  (input={s['input']})")
    t = availability_slot_tuesday()
    print(f"availability tuesday : {t['display']}  (input={t['input']})")
    w = availability_slot_wednesday()
    print(f"availability wednesday:{w['display']}  (input={w['input']})")
    g = group_session_date()
    print(f"group session monday : {g['display']}  (input={g['input']})")
    b = booking_slot()
    print(f"booking slot         : {b['display']}  day_num={b['day_num']}")
