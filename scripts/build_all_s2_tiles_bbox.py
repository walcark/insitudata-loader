"""
Download the official Sentinel-2 MGRS tiling grid (shapefile) and extract
all tile bounding boxes into a CSV file.

Source: https://github.com/justinelliotmeyers/Sentinel-2-Shapefile-Index
(converted from the official ESA KML tiling grid)
"""

import io
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests
from tqdm import tqdm

from insitudata_loader.satellites import Satellite

TILING_GRID_URL = (
    "https://github.com/justinelliotmeyers/Sentinel-2-Shapefile-Index"
    "/archive/refs/heads/master.zip"
)
EXTRACT_DIR = Path("/tmp/s2_tiles_grid/")
OUTPUT_PATH = Satellite.SENTINEL2.tiles_path


def download_and_extract(url: str, extract_dir: Path) -> None:
    print(f"Downloading tiling grid from:\n  {url}")
    response = requests.get(url, stream=True, timeout=300)
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))
    chunks = []
    with tqdm(total=total, unit="B", unit_scale=True, desc="Download") as pbar:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            chunks.append(chunk)
            pbar.update(len(chunk))

    data = b"".join(chunks)
    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        zf.extractall(extract_dir)
    print(f"Extracted to {extract_dir}")


def load_shapefile(extract_dir: Path) -> gpd.GeoDataFrame:
    shp_files = list(extract_dir.rglob("sentinel_2_index_shapefile.shp"))
    if not shp_files:
        raise FileNotFoundError(
            f"No sentinel_2_index_shapefile.shp found in {extract_dir}"
        )
    print(f"Reading shapefile: {shp_files[0]}")
    return gpd.read_file(shp_files[0])


def build_tiles_csv(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    print("Columns:", gdf.columns.tolist())

    # The shapefile uses 'Name' for tile ID
    tile_col = next(
        (
            c
            for c in gdf.columns
            if c.lower() in ("name", "tile", "tileid", "tile_id")
        ),
        gdf.columns[0],
    )
    print(f"Using '{tile_col}' as tile name column")

    bounds = gdf.geometry.bounds
    tile_names = gdf[tile_col].str.strip()
    # Ensure names start with "T"
    tile_names = tile_names.where(
        tile_names.str.startswith("T"), "T" + tile_names
    )

    df = pd.DataFrame(
        {
            "tile": tile_names.values,
            "lon_min": bounds["minx"].values,
            "lat_min": bounds["miny"].values,
            "lon_max": bounds["maxx"].values,
            "lat_max": bounds["maxy"].values,
        }
    )

    # Some tiles crossing the antimeridian have two rows — merge them
    df = (
        df.groupby("tile", sort=True)
        .agg(
            lon_min=("lon_min", "min"),
            lat_min=("lat_min", "min"),
            lon_max=("lon_max", "max"),
            lat_max=("lat_max", "max"),
        )
        .reset_index()
    )
    return df


if __name__ == "__main__":
    if not list(EXTRACT_DIR.rglob("sentinel_2_index_shapefile.shp")):
        download_and_extract(TILING_GRID_URL, EXTRACT_DIR)
    else:
        print(f"Shapefile already extracted in {EXTRACT_DIR}, skipping download.")

    gdf = load_shapefile(EXTRACT_DIR)
    print(f"Total tiles in grid: {len(gdf)}")

    df = build_tiles_csv(gdf)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} tiles to {OUTPUT_PATH}")
