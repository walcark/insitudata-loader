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

TMP_PATH = ROOT_PATH / ".tmp"
DATA_PATH = ROOT_PATH / "data"
CONFIG_PATH = ROOT_PATH / "config"
LOGGING_PATH = CONFIG_PATH / "logging.yaml"

# Sources
GLORIA_DATA_PATH = DATA_PATH / "sources/gloria_2022"

SATELLITES_PATH = DATA_PATH / "satellites"
