"""
paths.py

Author  : Kévin Walcarius
Date    : 2025-01-13
Version : 1.0
License : MIT
Summary : Useful paths for the library.
"""

from pathlib import Path


ROOT_PATH = Path(__file__).resolve().parent.parent.parent.parent

DATA_PATH = ROOT_PATH / "data"
CONFIG_PATH = ROOT_PATH / "config"
LOGGING_PATH = CONFIG_PATH / "logging.yaml"

# Sources
GLORIA_DATA_PATH = DATA_PATH / "sources/gloria_2022"

# Satellites
S2_DATA_PATH = DATA_PATH / "satellites/sentinel2"
S2_SRF_PATH = S2_DATA_PATH / "srf.csv"
S2_TILES_PATH = S2_DATA_PATH / "tiles_bbox_all.csv"
