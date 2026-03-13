"""
satellite.py

Author  : Kévin Walcarius
Date    : 2026-03-13
Version : 1.0
License : MIT
Summary : Satellite enum — single entry point for satellite identity and
          associated canonical data file paths.
"""

from enum import Enum
from pathlib import Path

from insitudata_loader.utils.paths import DATA_PATH


class Satellite(Enum):
    SENTINEL2 = "sentinel2"

    @property
    def data_path(self) -> Path:
        return DATA_PATH / "satellites" / self.value

    @property
    def srf_path(self) -> Path:
        return self.data_path / "srf.csv"

    @property
    def tiles_path(self) -> Path:
        return self.data_path / "tiles_bbox_all.csv"
