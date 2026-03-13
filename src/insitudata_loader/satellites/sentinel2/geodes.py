"""
geodes.py

Author  : Kévin Walcarius
Date    : 2026-03-13
Version : 1.0
License : MIT
Summary : Tools to perform API calls to the GEODES portal, and a pipeline
          step to search Sentinel-2 acquisitions for each in-situ sample.
          https://geodes-portal.cnes.fr/api/stac/items
"""

from typing import Any
from datetime import datetime
from enum import Enum

from pygeodes.utils.datetime_utils import (
    complete_datetime_from_str,
    datetime_to_str,
)
from pygeodes import Geodes, Config
from pygeodes.geodes import Item
from rich.progress import track
import pandas as pd

from insitudata_loader.core.data import InSituData
from insitudata_loader.utils.paths import CONFIG_PATH
from insitudata_loader.utils.logging import get_logger

get_logger(__name__)


class GeodesCollectionType(Enum):
    L1C = "PEPS_S2_L1C"
    L2A = "THEIA_REFLECTANCE_SENTINEL2_L2A"


def get_pygeodes_config(**kwargs: dict[str, Any]) -> Config:
    """
    Tries to load a PyGeodes Config from the config folder.
    Returns a default configuration if none is found.
    """
    cfile = CONFIG_PATH / "pygeodes_config.json"

    config = Config.from_file(str(cfile)) if cfile.exists() else Config()

    dictconfig = config.to_dict()
    dictconfig.update(**kwargs)

    return Config(**dictconfig)


def search_items_in_geodes(
    geodes: Geodes,
    collection: GeodesCollectionType,
    datemin: str | datetime,
    datemax: str | datetime,
    tile: str | None = None,
    max_cloud_cover: float | None = None,
    **additionnal_query: dict[str, Any],
) -> list[Item]:
    """
    Perform a query in a GEODES collection.

    Args:
        geodes (Geodes): the Geodes search instance.
        collection (GeodesCollectionType): the collection to search in.
        datemin (str | datetime): the minimum product date.
        datemax (str | datetime): the maximum product date.
        tile (str): the product tile.
        max_cloud_cover (float | None): the maximum cloud cover (%).

    Returns:
        list[Item]: the `pygeodes.Item` objects found.
    """
    if isinstance(datemin, datetime):
        datemin = datetime_to_str(datemin)
    datemin = complete_datetime_from_str(datemin)

    if isinstance(datemax, datetime):
        datemax = datetime_to_str(datemax)
    datemax = complete_datetime_from_str(datemax)

    query = {
        "start_datetime": {"gte": datemin},
        "end_datetime": {"lte": datemax},
        **additionnal_query,
    }
    if tile is not None:
        query.update({"grid:code": {"eq": tile}})

    if max_cloud_cover is not None:
        query.update({"eo:cloud_cover": {"lte": max_cloud_cover}})

    print(query)
    return geodes.search_items(
        query=query,
        collections=[collection.value],
        return_df=False,
        get_all=True,
    )


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
