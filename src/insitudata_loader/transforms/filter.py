"""
filter.py

Author  : Kévin Walcarius
Date    : 2026-03-13
Version : 1.0
License : MIT
Summary : Generic pipeline steps for filtering, date manipulation,
          and spatial tile location.
"""

from __future__ import annotations

import pandas as pd

from insitudata_loader.core.data import InSituData
from insitudata_loader.satellites.satellite import Satellite


class TilesLocator:
    """
    For all sample points in `insitu`, determines the satellite tile
    from longitude and latitude, using the canonical tiles CSV file for
    the given satellite (schema: tile, lon_min, lat_min, lon_max, lat_max).

    Parameters
    ----------
    satellite : Satellite
        The satellite whose tiling grid to use.
    """

    def __init__(self, satellite: Satellite):
        self.satellite = satellite

    def __call__(self, insitu: InSituData) -> InSituData:
        df_tiles = pd.read_csv(self.satellite.tiles_path)

        lon_min = df_tiles["lon_min"].to_numpy()
        lon_max = df_tiles["lon_max"].to_numpy()
        lat_min = df_tiles["lat_min"].to_numpy()
        lat_max = df_tiles["lat_max"].to_numpy()
        tile_names = df_tiles["tile"].to_numpy()

        tiles = []
        for _, row in insitu.df.iterrows():
            lon, lat = row["Longitude"], row["Latitude"]
            mask = (
                (lon >= lon_min)
                & (lon <= lon_max)
                & (lat >= lat_min)
                & (lat <= lat_max)
            )
            idx = mask.nonzero()[0]
            tiles.append(tile_names[idx[0]] if len(idx) > 0 else pd.NA)

        return insitu.add_column("tile", tiles)


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
