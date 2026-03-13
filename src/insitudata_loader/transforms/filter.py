"""
filter.py

Author  : Kévin Walcarius
Date    : 2026-03-13
Version : 1.0
License : MIT
Summary : Pipeline steps for filtering and date manipulation.
"""

import pandas as pd

from insitudata_loader.core.data import InSituData


class FilterDate:
    """
    Filters `insitu` points based on `Date_Time_UTC`, keeping only samples
    inside the interval [datemin, datemax].
    """

    def __init__(
        self,
        datemin: pd.Timestamp | str | None = None,
        datemax: pd.Timestamp | str | None = None,
    ):
        self.datemin = (
            pd.to_datetime(datemin) if datemin is not None else None
        )
        self.datemax = (
            pd.to_datetime(datemax) if datemax is not None else None
        )

    def __call__(self, insitu: InSituData) -> InSituData:
        date = pd.to_datetime(
            insitu.df["Date_Time_UTC"],
            format="%Y-%m-%dT%H:%M",
            errors="coerce",
        )

        mask = pd.Series(True, index=insitu.df.index)

        if self.datemin is not None:
            mask &= date >= self.datemin

        if self.datemax is not None:
            mask &= date <= self.datemax

        idx = insitu.df.index[mask]
        return insitu.filter(idx)


class ComputeDayBounds:
    """
    Computes day bounds (`datemin`, `datemax`) for each sample based on
    `Date_Time_UTC`, where `datemin` is floored to the day, and `datemax`
    is the next day.
    """

    def __call__(self, insitu: InSituData) -> InSituData:
        date = pd.to_datetime(
            insitu.df["Date_Time_UTC"],
            format="%Y-%m-%dT%H:%M",
            errors="coerce",
        )

        datemin = date.dt.floor("D")
        datemax = datemin + pd.Timedelta(days=1)

        out = insitu.add_column("datemin", datemin)
        return out.add_column("datemax", datemax)
