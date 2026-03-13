"""
srf.py

Author  : Kévin Walcarius
Date    : 2026-03-13
Version : 1.0
License : MIT
Summary : Generic loader for satellite Spectral Response Function files.

Expected CSV schema
-------------------
wavelength  (index) : integer wavelength in nm
{SAT}_{BAND}        : one column per satellite/band pair
                      e.g. S2A_B1, S2A_B2, ..., S2B_B1, ..., L8_B1, ...
"""

from pathlib import Path

import numpy as np
import pandas as pd


class SRF:
    """
    Loads a Spectral Response Function CSV and convolves spectra onto
    satellite bands.

    Parameters
    ----------
    filepath : Path
        Path to a CSV file following the canonical SRF schema.

    Attributes
    ----------
    SATELLITES : list[str]
        Satellite identifiers derived from column names (e.g. ["S2A", "S2B"]).
    """

    def __init__(self, filepath: Path):
        df = pd.read_csv(filepath, index_col="wavelength")
        self._df = df
        self.SATELLITES: list[str] = sorted(
            {col.rsplit("_", 1)[0] for col in df.columns}
        )

    def convolve(self, spectrum: pd.Series, band: str, satellite: str) -> float:
        """
        Convolve `spectrum` with the SRF of `band` for `satellite`.

        Parameters
        ----------
        spectrum : pd.Series
            Rrs values indexed by integer wavelength (nm).
        band : str
            Band name, e.g. "B2", "B3".
        satellite : str
            Satellite identifier, e.g. "S2A", "S2B".

        Returns
        -------
        float
            Band-integrated Rrs value, or np.nan if no overlap.
        """
        col = f"{satellite}_{band}"
        srf = self._df[col]

        common = spectrum.index.intersection(srf.index)
        if len(common) == 0:
            return np.nan

        srf_vals = srf.loc[common].to_numpy(dtype=float)
        rrs_vals = spectrum.loc[common].to_numpy(dtype=float)

        valid = ~np.isnan(rrs_vals)
        denom = srf_vals[valid].sum()
        if denom == 0:
            return np.nan

        return float((rrs_vals[valid] * srf_vals[valid]).sum() / denom)
