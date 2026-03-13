"""
loader.py

Author  : Kévin Walcarius
Date    : 2026-03-13
Version : 1.0
License : MIT
Summary : File paths for the GLORIA 2022 dataset.
"""

from insitudata_loader.utils.paths import GLORIA_DATA_PATH

GLORIA_FILES = [
    GLORIA_DATA_PATH / "GLORIA_meta_and_lab.csv",
    GLORIA_DATA_PATH / "GLORIA_Rrs_mean.csv",
    GLORIA_DATA_PATH / "GLORIA_Rrs_std.csv",
    GLORIA_DATA_PATH / "GLORIA_Rrs.csv",
]
