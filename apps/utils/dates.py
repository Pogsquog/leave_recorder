from datetime import date, timedelta


def get_month_end_date(year: int, month: int) -> date:
    """Return the last day of the given month."""
    if month == 12:
        return date(year + 1, 1, 1) - timedelta(days=1)
    return date(year, month + 1, 1) - timedelta(days=1)


def get_month_start_date(year: int, month: int) -> date:
    """Return the first day of the given month."""
    return date(year, month, 1)
