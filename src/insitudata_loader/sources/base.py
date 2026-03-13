"""
base.py

Author  : Kévin Walcarius
Date    : 2026-03-13
Version : 1.0
License : MIT
Summary : Abstract base class for all in-situ data source adapters.
"""

from abc import ABC, abstractmethod

from insitudata_loader.core.data import InSituData


class DataSourceAdapter(ABC):
    """
    Contract that every data source must implement.
    A concrete adapter is responsible for loading raw source files
    and returning a normalized `InSituData` instance.
    """

    @abstractmethod
    def load(self) -> InSituData: ...
