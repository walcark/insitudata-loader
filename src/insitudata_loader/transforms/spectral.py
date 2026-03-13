"""
spectral.py

Author  : Kévin Walcarius
Date    : 2026-03-13
Version : 1.0
License : MIT
Summary : Generic pipeline step for convolving full spectra onto satellite
          bands using any Spectral Response Function object.
"""

import pandas as pd

from insitudata_loader.core.data import InSituData


class ConvolveToSatelliteBands:
    """
    For each sample, convolves the full Rrs spectrum with the Spectral
    Response Function of each requested band and satellite.
    Adds columns named `Rrs_<sat>_<band>` to the dataset.

    The spectral columns are identified via `insitu.spectral_col_prefix`.

    Parameters
    ----------
    srf :
        Any object with a `.convolve(spectrum, band, satellite) -> float`
        method and a `.SATELLITES` attribute listing supported satellites.
    bands : list[str]
        Bands to compute, e.g. ["B1", "B2"].
    sat : list[str] | None
        Satellites to compute, e.g. ["S2A", "S2B"]. Defaults to all
        satellites defined in `srf.SATELLITES`.
    """

    def __init__(self, srf, bands: list[str], sat: list[str] | None = None):
        self.srf = srf
        self.bands = bands
        self.sat = sat if sat is not None else list(srf.SATELLITES)

    def __call__(self, insitu: InSituData) -> InSituData:
        prefix = insitu.spectral_col_prefix or ""
        rrs_cols = [
            c for c in insitu.df.columns if c.startswith(prefix)
        ]
        wavelengths = [int(c.removeprefix(prefix)) for c in rrs_cols]

        result = insitu
        for sat in self.sat:
            for band in self.bands:
                values = []
                for _, row in result.df.iterrows():
                    spectrum = pd.Series(
                        row[rrs_cols].to_numpy(dtype=float),
                        index=wavelengths,
                    )
                    values.append(self.srf.convolve(spectrum, band, sat))
                result = result.add_column(f"Rrs_{sat}_{band}", values)

        s2_cols = [
            f"Rrs_{sat}_{band}"
            for sat in self.sat
            for band in self.bands
        ]
        valid_idx = result.df.dropna(subset=s2_cols).index
        result = result.filter(valid_idx)

        result.df = result.df.drop(columns=rrs_cols)
        result.args = list(result.df.columns)

        return result
