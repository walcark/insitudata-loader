"""
adapter.py

Author  : Kévin Walcarius
Date    : 2026-03-13
Version : 1.0
License : MIT
Summary : Adapter that converts the GLORIA dataset to the internal
          InSituData format.
"""

from insitudata_loader.core.data import InSituData
from insitudata_loader.sources.base import DataSourceAdapter
from .loader import GLORIA_FILES


class GloriaAdapter(DataSourceAdapter):
    """
    Loads the GLORIA 2022 in-situ dataset and returns a normalized
    `InSituData` instance.

    Parameters
    ----------
    keep_nan : bool
        If False (default), rows with NaN in mandatory columns are dropped.
    """

    MANDATORY_ARGS = [
        "Latitude",
        "Longitude",
        "Date_Time_UTC",
        "Skyglint_removal",
        "Bias_removal_in_NIR",
        "Self_shading_correction",
    ]
    OPTIONAL_ARGS = [
        "Distance_to_shore",
        "Cloud_fraction",
        "AOT",
    ]

    def __init__(self, keep_nan: bool = False):
        self.keep_nan = keep_nan

    def load(self) -> InSituData:
        return InSituData(
            filepath=GLORIA_FILES,
            mandatory_args=self.MANDATORY_ARGS,
            optional_args=self.OPTIONAL_ARGS,
            spectral_col_prefix="Rrs_mean_",
            keep_nan=self.keep_nan,
        )
