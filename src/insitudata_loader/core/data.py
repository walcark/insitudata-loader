"""
insitu_data.py

Author  : Kévin Walcarius
Date    : 2025-01-16
Version : 1.0
License : MIT
Summary : Dataclass to represent any type of in-situ measurement
          of radiometric quantities.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import pandas as pd
import numpy as np
import copy

from insitudata_loader.utils import check_columns

# TODO: ajouter un filtre de NaN en ligne et colonne (selon l'usage)


@dataclass
class InSituData:
    filepath: Path | list[Path]
    mandatory_args: list[str]
    optional_args: list[str] | None = None
    keep_nan: bool = True
    spectral_col_prefix: str | None = None
    df: pd.DataFrame | None = None

    def __post_init__(self):
        """
        Load data, check the mandatory args and filter
        nan if required.
        """
        if isinstance(self.filepath, Path):
            self.filepath = [self.filepath]

        assert all(f.exists() for f in self.filepath)
        self.df = self.load_data(self.mandatory_args, self.optional_args)
        self._dropna()

        self.args = list(self.df.columns)

    def load_data(
        self,
        mandatory_args: list[str] | None = None,
        optional_args: list[str] | None = None,
    ) -> pd.DataFrame:
        """
        Load in-situ data from `self.filename`, only for the current
        indexes of `self.df`. If no `mandatory_args` are provided, keep
        all columns from the original database.
        `optional_args` are loaded but excluded from NaN filtering.
        """
        dfs: list[pd.DataFrame] = [pd.read_csv(f) for f in self.filepath]

        df = dfs[0].copy()
        for d in dfs[1:]:
            new_cols = d.columns.difference(df.columns)
            df = pd.concat([df, d.loc[:, new_cols]], axis=1)

        if self.df is not None:
            df = df.loc[self.df.index]
            new_cols = self.df.columns.difference(df.columns)
            df = pd.concat([df, self.df.loc[:, new_cols]], axis=1)

        if mandatory_args is not None:
            check_columns(df, mandatory_args)
            cols = list(mandatory_args)
            if self.spectral_col_prefix is not None:
                spectral_cols = [
                    c for c in df.columns
                    if c.startswith(self.spectral_col_prefix)
                ]
                cols += spectral_cols
            if optional_args is not None:
                check_columns(df, optional_args)
                cols += [c for c in optional_args if c not in cols]
            return df.loc[:, cols]

        return df

    def add_column(self, arg: str, values: list[Any]) -> InSituData:
        """
        Add a column to the data. Raise an error if the new column is not
        consistent with the length of `self.df`.
        """
        assert len(values) == len(self.df)

        new = copy.copy(self)
        new.df = self.df.copy()

        new.df.insert(1, arg, np.asarray(values))
        new._dropna()
        new.args = list(new.df.columns)

        return new

    def filter(self, index: pd.Index) -> "InSituData":
        """
        Return a new InSituData restricted to `index`.
        """
        assert self.df is not None, (
            "InSituData.df is None; nothing to filter."
        )

        # Vérif légère que l'index demandé existe bien
        missing = index.difference(self.df.index)
        assert len(missing) == 0, (
            f"Some indices are not in df.index: {list(missing[:10])}"
        )

        new = copy.copy(self)
        new.df = self.df.loc[index].copy()

        new._dropna()
        new.args = list(new.df.columns)

        return new

    def _dropna(self) -> None:
        if not self.keep_nan and self.df is not None:
            self.df = self.df.replace(
                {"nan": np.nan, "NaN": np.nan, "": np.nan}
            )
            subset = self.mandatory_args if self.mandatory_args else None
            self.df = self.df.dropna(subset=subset)

    def save(self, filepath: Path) -> None:
        self.df.to_csv(filepath)
