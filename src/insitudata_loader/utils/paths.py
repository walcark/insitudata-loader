"""
paths.py

Author  : Kévin Walcarius
Date    : 2025-01-13
Version : 1.0
License : MIT
Summary : Useful paths for the library.
"""

from pathlib import Path


ROOT_PATH = Path(__file__).resolve().parent.parent.parent.parent

DATA_PATH = ROOT_PATH / "data"
GLORIA_DATA_PATH = DATA_PATH / "gloria_2022"
CONFIG_PATH = ROOT_PATH / "config"
LOGGING_PATH = ROOT_PATH / "config/logging.yaml"
