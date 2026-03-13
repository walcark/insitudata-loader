"""
time_utils.py

Author  : Kévin Walcarius
Date    : 2026-03-13
Version : 1.0
License : MIT
Summary : Utility functions for time operations.
"""

from datetime import datetime, timedelta, date
from typing import List, Tuple, Union


DateLike = Union[str, date]


def to_str(d: DateLike, out_ftm: str = "%Y-%m-%d") -> str:
    """
    Normalize a date or date-string into 'YYYYMMDD'.
    Supports date, datetime, or strings in 'YYYYMMDD' or 'YYYY-MM-DD'.
    """
    if isinstance(d, date):
        return d.strftime(out_ftm)
    for fmt in ("%Y%m%d", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(d, fmt)
            return dt.strftime(out_ftm)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {d!r}")


def to_date(date: str, in_fmt: str = "%Y-%m-%d") -> date:
    """Wrap strptime for accordance with `to_str`."""
    return datetime.strptime(date, in_fmt)


def regular_timestamps(
    datemin: DateLike, datemax: DateLike, delta: int
) -> List[str]:
    """
    Build list of regular timestamps within a time interval.
    """
    start = to_date(datemin)
    end = to_date(datemax)
    n_stamps = (end - start) // timedelta(days=delta)
    date_keys = [
        to_str(start + i * timedelta(days=delta)) for i in range(n_stamps)
    ]
    return date_keys


def find_close_dates(
    dates: List[DateLike], max_delta_days: float = 5
) -> List[Tuple[DateLike, DateLike]]:
    """
    For a given list of dates, returns all the unique pairs of close dates.
    """
    if isinstance(dates[0], str):
        chtype = True
    dates_cpy = [to_date(d) for d in dates] if chtype else dates
    dates_cpy = sorted(dates_cpy)
    N: int = len(dates_cpy)
    pairs: set = set()
    idx, idy = 0, 1
    while idy < N:  # Traveling dates with two pointers
        valx = dates[idx]
        valy = dates[idy]
        while abs(valy - valx) <= timedelta(days=max_delta_days):
            if chtype:
                pairs.add((to_str(valx), to_str(valy)))
            else:
                pairs.add((valx, valy))
            idy += 1
            if idy >= len(dates):
                break
            valy = dates[idy]
        idx += 1
    return list(pairs)


def create_periods_for_cpu(
    fromdate: str, todate: str, n_cpu: int
) -> List[Tuple[datetime, datetime]]:
    """
    Creates a list of 'n_cpu' time intervals from a single time interval.
    """
    dt_start = datetime.strptime(fromdate, "%Y-%m-%d")
    dt_end = datetime.strptime(todate, "%Y-%m-%d")
    total_days = (dt_end - dt_start).days + 1
    base_days = total_days // n_cpu
    extra = total_days % n_cpu

    tranches = []
    cur_start = dt_start
    for i in range(n_cpu):
        days_i = base_days + (1 if i < extra else 0)
        cur_end = min(cur_start + timedelta(days=days_i - 1), dt_end)
        tranches.append((cur_start, cur_end))
        cur_start = cur_end + timedelta(days=1)

    return tranches


if __name__ == "__main__":
    mini = "20220101"
    maxi = "20220501"

    print(regular_timestamps(mini, maxi, delta=5))
