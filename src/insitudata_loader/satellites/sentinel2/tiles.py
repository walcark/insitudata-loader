"""
tiles.py

Author  : Kévin Walcarius
Date    : 2026-03-13
Version : 1.0
License : MIT
Summary : Locates the Sentinel-2 MGRS tile for each in-situ sample.
"""

import pandas as pd

from insitudata_loader.core.data import InSituData
from insitudata_loader.utils.paths import S2_TILES_PATH


class TilesLocator:
    """
    For all sample points in `insitu`, determines the Sentinel-2 tile
    location from longitude and latitude information.
    """

    def __call__(self, insitu: InSituData) -> InSituData:
        df_tiles = pd.read_csv(S2_TILES_PATH)

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
