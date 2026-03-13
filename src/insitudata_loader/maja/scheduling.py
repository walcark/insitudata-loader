import pandas as pd

from insitudata_loader.core.data import InSituData


def schedule_maja(
    dataset: InSituData,
    name: str,
    month_max_dist: int = 1,
) -> list[dict]:
    """
    Segment an InSituData dataset by tile, then group each tile's measurement
    dates into temporal intervals where consecutive dates are less than 1 month
    apart.

    Parameters
    ----------
    dataset : InSituData
        Must have "tile" (from TilesLocator) and "Date_Time_UTC" columns.
    name : str
        Experience name attached to all scheduling entries.
    month_max_dist : int
        Maximum number of month between two consecutive dates in a group.
        If month_max_dist=1, dates separated by more than one month will
        be dispatched in differents groups.

    Returns
    -------
    list[dict[str, str]]
        List of arguments dictionnaries for the launch of Maja and L1C
        queries.

    """
    df = dataset.df
    dates = pd.to_datetime(df["Date_Time_UTC"], errors="coerce")
    df = df.copy()
    df["_date"] = dates

    result = []

    for tile, group in df.groupby("tile"):
        if pd.isna(tile):
            continue

        sorted_dates = sorted(group["_date"].dropna().unique())
        if not sorted_dates:
            continue

        groups: list[list[pd.Timestamp]] = []
        current: list[pd.Timestamp] = [sorted_dates[0]]

        for date in sorted_dates[1:]:
            if date < current[-1] + pd.DateOffset(months=month_max_dist):
                current.append(date)
            else:
                groups.append(current)
                current = [date]
        groups.append(current)

        for g in groups:
            fromdate = min(g) - pd.DateOffset(months=month_max_dist)
            todate = max(g) + pd.DateOffset(days=5)
            result.append(
                {
                    "tile": tile,
                    "site": name,
                    "fromdate": fromdate.strftime("%Y-%m-%d"),
                    "todate": todate.strftime("%Y-%m-%d"),
                }
            )

    return result
