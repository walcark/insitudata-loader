"""
pandas_utils.py

Author  : Kévin Walcarius
Date    : 2025-01-13
Version : 1.0
License : MIT
Summary : Useful methods in pandas.
"""

import pandas as pd


def check_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
    """
    Ensures that all `required_columns` are in the input pandas
    DataFrame.
    """
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")
