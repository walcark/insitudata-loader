from pygeodes import Geodes
import pandas as pd

from insitudata_loader.satellites import (
    Satellite,
    GeodesCollectionType,
    get_pygeodes_config,
    search_items_in_geodes,
)


def create_tile_and_extent_file() -> None:
    """
    Query all possible tiles from GEODES portal, and their associated
    bounding box. Format those tiles as a .csv file.
    """
    items = search_items_in_geodes(
        geodes=Geodes(conf=get_pygeodes_config()),
        collection=GeodesCollectionType.S2_L2A,
        datemin="2020-01-01",
        datemax="2020-01-10",
    )

    tile_to_bbox = {}
    for item in items:
        d = item.to_dict()
        tile = d["properties"]["grid:code"]
        bbox = d["bbox"]
        tile_to_bbox[tile] = bbox

    data = {
        "tile": list(tile_to_bbox.keys()),
        "bbox": list(tile_to_bbox.values()),
    }

    df_tiles = pd.DataFrame(data)

    df_tiles[["lon_min", "lat_min", "lon_max", "lat_max"]] = pd.DataFrame(
        df_tiles["bbox"].tolist(), index=df_tiles.index
    )

    df_tiles = df_tiles.drop(columns=["bbox"])
    df_tiles = df_tiles.sort_values("tile").reset_index(drop=True)

    df_tiles.to_csv(
        Satellite.SENTINEL2.data_path / "tiles_bbox.csv", index=False
    )


if __name__ == "__main__":
    create_tile_and_extent_file()
