"""
transform_insitu_data.py

Author  : Kévin Walcarius
Date    : 2025-01-16
Version : 1.0
License : MIT
Summary : Methods to transform InSituData instance.
"""

from pathlib import Path
from rich.progress import track
from pygeodes import Geodes
import matplotlib.pyplot as plt
import pandas as pd

from insitudata_loader.utils import (
    get_pygeodes_config,
    search_items_in_geodes,
    GeodesCollectionType,
    DATA_PATH,
    S2SRF,
)
from .data import InSituData


class TilesLocator:
    """
    For all sample points in `insitu`, determines the Sentinel-2 tile
    location from longitude and latitude information.
    """

    def __call__(self, insitu: InSituData) -> InSituData:
        df_tiles = pd.read_csv(DATA_PATH / "sentinel2/tiles_bbox_all.csv")

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


class ComputeS2BandRrs:
    """
    For each sample, convolves the full Rrs_mean spectrum with the
    Spectral Response Function of each requested Sentinel-2 band.
    Adds columns named `Rrs_<sat>_<band>` to the dataset.

    Parameters
    ----------
    bands : list[str]
        Bands to compute, e.g. ["B1", "B2"].
    sat : list[str] | None
        Satellites to compute, e.g. ["S2A", "S2B"]. Defaults to all.
    """

    def __init__(self, bands: list[str], sat: list[str] | None = None):
        self.bands = bands
        self.sat = sat if sat is not None else S2SRF.SATELLITES
        self.srf = S2SRF()

    def __call__(self, insitu: InSituData) -> InSituData:
        rrs_cols = [
            c for c in insitu.df.columns if c.startswith("Rrs_mean_")
        ]
        wavelengths = [int(c.removeprefix("Rrs_mean_")) for c in rrs_cols]

        result = insitu
        for sat in self.sat:
            for band in self.bands:
                values = []
                for _, row in result.df.iterrows():
                    spectrum = pd.Series(
                        row[rrs_cols].to_numpy(dtype=float),
                        index=wavelengths,
                    )
                    values.append(self.srf.convolve(spectrum, band, sat))
                result = result.add_column(f"Rrs_{sat}_{band}", values)

        s2_cols = [
            f"Rrs_{sat}_{band}"
            for sat in self.sat
            for band in self.bands
        ]
        valid_idx = result.df.dropna(subset=s2_cols).index
        result = result.filter(valid_idx)

        result.df = result.df.drop(columns=rrs_cols)
        result.args = list(result.df.columns)

        return result


class PlotRrs:
    """
    Plots Rrs columns for the requested satellites and bands, with optional
    metadata subplots stacked above. Passes data through unchanged.

    Parameters
    ----------
    sat : list[str] | None
        Satellites to plot, e.g. ["S2A", "S2B"]. Defaults to all found.
    bands : list[str] | None
        Bands to plot, e.g. ["B1", "B3"]. Defaults to all found.
    metadata : list[str] | None
        Column names to plot as subplots above the Rrs plot, one per row.
    """

    def __init__(
        self,
        sat: list[str] | None = None,
        bands: list[str] | None = None,
        metadata: list[str] | None = None,
    ):
        self.sat = sat
        self.bands = bands
        self.metadata = metadata or []

    def __call__(self, insitu: InSituData) -> InSituData:
        rrs_cols = [
            c for c in insitu.df.columns
            if c.startswith("Rrs_S2A_") or c.startswith("Rrs_S2B_")
        ]

        if self.sat is not None:
            rrs_cols = [
                c for c in rrs_cols
                if any(c.startswith(f"Rrs_{s}_") for s in self.sat)
            ]
        if self.bands is not None:
            rrs_cols = [
                c for c in rrs_cols
                if any(c.endswith(f"_{b}") for b in self.bands)
            ]

        x = insitu.df.reset_index(drop=True).index
        nrows = 1 + len(self.metadata)

        fig, axes = plt.subplots(
            nrows=nrows,
            ncols=1,
            sharex=True,
            gridspec_kw={"hspace": 0},
        )
        if nrows == 1:
            axes = [axes]

        for ax, col in zip(axes, self.metadata):
            ax.plot(x, insitu.df[col].reset_index(drop=True))
            ax.set_ylabel(col)
            ax.tick_params(labelbottom=False)

        ax_rrs = axes[-1]
        for col in rrs_cols:
            label = col.removeprefix("Rrs_")
            ax_rrs.plot(x, insitu.df[col].reset_index(drop=True), label=label)
        ax_rrs.set_xlabel("Ligne")
        ax_rrs.set_ylabel("Rrs")
        ax_rrs.legend()

        plt.show()

        return insitu


class SaveToCsv:
    """
    Saves the current dataset to a CSV file at `filepath` and passes
    the data through unchanged, so it can be chained in a pipeline.
    """

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)

    def __call__(self, insitu: InSituData) -> InSituData:
        insitu.save(self.filepath)
        return insitu


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
