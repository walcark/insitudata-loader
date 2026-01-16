from pygeodes import Geodes
import pandas as pd

from insitudata_loader.utils import DATA_PATH
from insitudata_loader.utils import (
    search_items_in_geodes,
    get_pygeodes_config,
    GeodesCollectionType,
)


def create_tile_and_extent_file() -> None:
    """
    Query all possible tiles from GEODES portal, and their associated
    bounding box. Format those tiles as a .csv file.
    """
    # Search all L2A items for 10 consecutive days
    items = search_items_in_geodes(
        geodes=Geodes(conf=get_config()),
        collection=GeodesCollectionType.L2A,
        datemin="2020-01-01",
        datemax="2020-01-10",
    )

    # Keep only unique tile ID and their associated bbox
    tile_to_bbox = {}
    for item in items:
        d = item.to_dict()
        tile = d["properties"]["grid:code"]
        bbox = d["bbox"]
        tile_to_bbox[tile] = bbox  # écrase si déjà présent
    data = {
        "tile": list(tile_to_bbox.keys()),
        "bbox": list(tile_to_bbox.values()),
    }

    # Format the dictionnary as a pandas dataframe
    df_tiles = pd.DataFrame(data)

    df_tiles[["lon_min", "lat_min", "lon_max", "lat_max"]] = pd.DataFrame(
        df_tiles["bbox"].tolist(), index=df_tiles.index
    )

    df_tiles = df_tiles.drop(columns=["bbox"])
    df_tiles = df_tiles.sort_values("tile").reset_index(drop=True)

    df_tiles.to_csv(DATA_PATH / "sentinel2/tiles_bbox.csv", index=False)


if __name__ == "__main__":
    create_tile_and_extent_file()
