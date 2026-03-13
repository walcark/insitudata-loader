"""
export.py

Author  : Kévin Walcarius
Date    : 2026-03-13
Version : 1.0
License : MIT
Summary : Pipeline steps for saving and plotting data.
"""

from pathlib import Path

import matplotlib.pyplot as plt

from insitudata_loader.core.data import InSituData


class SaveToCsv:
    """
    Saves the current dataset to a CSV file at `filepath` and passes
    the data through unchanged, so it can be chained in a pipeline.
    """

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)

    def __call__(self, insitu: InSituData) -> InSituData:
        insitu.save(self.filepath)
        return insitu


class PlotRrs:
    """
    Plots Rrs columns for the requested satellites and bands, with optional
    metadata subplots stacked above. Passes data through unchanged.

    Parameters
    ----------
    sat : list[str] | None
        Satellites to plot, e.g. ["S2A", "S2B"]. Defaults to all found.
    bands : list[str] | None
        Bands to plot, e.g. ["B1", "B3"]. Defaults to all found.
    metadata : list[str] | None
        Column names to plot as subplots above the Rrs plot, one per row.
    """

    def __init__(
        self,
        sat: list[str] | None = None,
        bands: list[str] | None = None,
        metadata: list[str] | None = None,
    ):
        self.sat = sat
        self.bands = bands
        self.metadata = metadata or []

    def __call__(self, insitu: InSituData) -> InSituData:
        rrs_cols = [
            c for c in insitu.df.columns
            if c.startswith("Rrs_S2A_") or c.startswith("Rrs_S2B_")
        ]

        if self.sat is not None:
            rrs_cols = [
                c for c in rrs_cols
                if any(c.startswith(f"Rrs_{s}_") for s in self.sat)
            ]
        if self.bands is not None:
            rrs_cols = [
                c for c in rrs_cols
                if any(c.endswith(f"_{b}") for b in self.bands)
            ]

        x = insitu.df.reset_index(drop=True).index
        nrows = 1 + len(self.metadata)

        fig, axes = plt.subplots(
            nrows=nrows,
            ncols=1,
            sharex=True,
            gridspec_kw={"hspace": 0},
        )
        if nrows == 1:
            axes = [axes]

        for ax, col in zip(axes, self.metadata):
            ax.plot(x, insitu.df[col].reset_index(drop=True))
            ax.set_ylabel(col)
            ax.tick_params(labelbottom=False)

        ax_rrs = axes[-1]
        for col in rrs_cols:
            label = col.removeprefix("Rrs_")
            ax_rrs.plot(x, insitu.df[col].reset_index(drop=True), label=label)
        ax_rrs.set_xlabel("Ligne")
        ax_rrs.set_ylabel("Rrs")
        ax_rrs.legend()

        plt.show()

        return insitu
