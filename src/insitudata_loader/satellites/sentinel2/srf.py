"""
srf.py

Author  : Kévin Walcarius
Date    : 2026-03-13
Version : 1.0
License : MIT
Summary : Utility class to load Sentinel-2 Spectral Response Functions
          and convolve in-situ Rrs spectra onto S2 bands.
"""

import numpy as np
import pandas as pd

from insitudata_loader.utils.paths import S2_SRF_PATH


class S2SRF:
    """
    Loads the ESA Sentinel-2 Spectral Response Functions (SRF) and
    provides a method to convolve a Rrs spectrum onto a given S2 band.

    Usage:
        srf = S2SRF()
        rrs_b3 = srf.convolve(spectrum, band="B3", satellite="S2A")
    """

    SATELLITES = ("S2A", "S2B")
    _SHEETS = {
        "S2A": "Spectral Responses (S2A)",
        "S2B": "Spectral Responses (S2B)",
    }

    def __init__(self):
        self._srf: dict[str, pd.DataFrame] = {}
        for sat in self.SATELLITES:
            df = pd.read_excel(
                S2_SRF_PATH,
                sheet_name=self._SHEETS[sat],
                engine="odf",
            )
            df = df.set_index("SR_WL")
            self._srf[sat] = df

    def convolve(
        self, spectrum: pd.Series, band: str, satellite: str
    ) -> float:
        """
        Convolve `spectrum` with the SRF of `band` for `satellite`.

        Parameters
        ----------
        spectrum : pd.Series
            Rrs values indexed by integer wavelength (nm).
        band : str
            S2 band name, e.g. "B2", "B3", "B8A".
        satellite : str
            "S2A" or "S2B".

        Returns
        -------
        float
            Band-integrated Rrs value, or np.nan if no overlap.
        """
        col = f"{satellite}_SR_AV_{band}"
        srf = self._srf[satellite][col]

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
