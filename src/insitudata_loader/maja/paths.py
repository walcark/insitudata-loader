"""
paths.py

Author  : Kévin Walcarius
Date    : 2026-03-13
Version : 1.0
License : MIT
Summary : All important path for Maja related operations on Trex.
"""

from pathlib import Path

from insitudata_loader.utils import TMP_PATH

# Maja related folders on TREX
MAJA_ROOT = Path("/work/CESBIO/projects/Maja")
L1C_ROOT = MAJA_ROOT / "L1C"
L2A_ROOT = MAJA_ROOT / "L2A_MAJA"
CONF_ROOT = TMP_PATH / "conf"

# CAMS and DTM folders
DTM_ROOT = MAJA_ROOT / "DTM_120"
CAMS_ROOT = Path("/work/datalake/CAMS_MAJA/startmaja_format")

# Root of the folder where the Amalthee launcher is located
TREX_EXT_ROOT = "/home/uz/walcark/PARA/ressources/trex_external_libs"
