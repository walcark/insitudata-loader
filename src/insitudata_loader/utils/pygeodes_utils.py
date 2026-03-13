"""
geodes_api.py

Author  : Kévin Walcarius
Date    : 2025-01-13
Version : 1.0
License : MIT
Summary : Tools to perform API calls to the GEODES portal.
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

from insitudata_loader.utils import CONFIG_PATH, get_logger

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
    # Ensure dates are readable by the GEODES API
    if isinstance(datemin, datetime):
        datemin = datetime_to_str(datemin)
    datemin = complete_datetime_from_str(datemin)

    if isinstance(datemax, datetime):
        datemax = datetime_to_str(datemax)
    datemax = complete_datetime_from_str(datemax)

    # Build query
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
    # Launch search
    return geodes.search_items(
        query=query,
        collections=[collection.value],
        return_df=False,
        get_all=True,
    )
