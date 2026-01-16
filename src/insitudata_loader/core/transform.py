"""
transform_insitu_data.py

Author  : Kévin Walcarius
Date    : 2025-01-16
Version : 1.0
License : MIT
Summary : Methods to transform InSituData instance.
"""

from rich.progress import track
from pygeodes import Geodes
import pandas as pd

from insitudata_loader.utils import (
    get_pygeodes_config,
    search_items_in_geodes,
    GeodesCollectionType,
    DATA_PATH,
)
from .data import InSituData


class TilesLocator:
    """
    For all sample points in `insitu`, determines the Sentinel-2 tile
    location from longitude and latitude information.
    """

    def __call__(self, insitu: InSituData) -> InSituData:
        df_tiles = pd.read_csv(DATA_PATH / "sentinel2/tiles_bbox.csv")

        df_pts = (
            insitu.df.copy()
            .reset_index(drop=False)
            .rename(columns={"index": "pt"})
        )

        cross = df_pts.merge(df_tiles, how="cross")

        inside = (
            (cross["Longitude"] >= cross["lon_min"])
            & (cross["Longitude"] <= cross["lon_max"])
            & (cross["Latitude"] >= cross["lat_min"])
            & (cross["Latitude"] <= cross["lat_max"])
        )

        matches = cross.loc[inside, ["pt", "tile"]].drop_duplicates("pt")

        out = (
            df_pts.merge(matches, on="pt", how="left")
            .set_index("pt", drop=True)
            .sort_index()
        )

        return insitu.add_column("tile", out["tile"].to_list())


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


class SearchOnGeodes:
    """
    Searches GEODES items for each sample (tile + day bounds),
    and adds a new column named after `collection_type.name`.
    """

    def __init__(
        self,
        max_cloud: float,
        collection_type: GeodesCollectionType,
    ):
        self.max_cloud = max_cloud
        self.collection_type = collection_type

    def __call__(self, insitu: InSituData) -> InSituData:
        df = insitu.df.copy()

        geodes = Geodes(conf=get_pygeodes_config())

        new_col = []
        it = df.iterrows()

        for _, row in track(it, total=len(df), description="GEODES search"):
            items = search_items_in_geodes(
                collection=self.collection_type,
                datemin=getattr(row, "datemin"),
                datemax=getattr(row, "datemax"),
                tile=getattr(row, "tile"),
                max_cloud_cover=self.max_cloud,
                geodes=geodes,
            )

            new_col.append(items[0] if len(items) >= 1 else pd.NA)

        return insitu.add_column(self.collection_type.name, new_col)
