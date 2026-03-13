"""
l2a.py

Author  : Kévin Walcarius
Date    : 2026-03-13
Version : 1.0
License : MIT
Summary : Command to launch the computation of MAJA L2A images on TREX.
"""

import subprocess
import os

from .paths import CONF_ROOT, CAMS_ROOT, L1C_ROOT, L2A_ROOT, DTM_ROOT
from .slurm_commands import slurm_maja, maja_input_folders
import insitudata_loader.utils as utils

logger = utils.get_logger(__name__)


def build_slurm_to_launch_maja(
    site: str,
    tile_id: str,
    fromdate: str,
    todate: str,
    run: bool = False,
    maja_version: str = "4.10.0",
    noenv: bool = False,
    nocir: bool = False,
    with_cams: bool = True,
) -> None:
    """
    Creates and saves a SLURM submit script (.slm) to launch Maja
    for a given time range. Launches maja is run is True.

    Parameters
    ----------
    site (str):
        Alias for the site of interest (e.g., Toulouse).
    tile_id (str):
        L1C identifier of the tile (e.g., 31TCJ).
    fromdate (str):
        Start date in "YYYY-MM-DD" format.
    todate (str):
        End date in "YYYY-MM-DD" format.
    run (bool):
        If True, submit each generated script with `sbatch`.
    noenv (bool):
        If True, doesn't correct for ajdacency effects.
    nocir (bool):
        If True, does not apply cirrus correction.

    Returns
    -------
    Tuple[List[str], List[str]]:
        A tuple of two lists:
        - The first list contains the paths to the generated SLURM script.
        - The second list contains the corresponding output L2A path.
    """
    # If cams Maja, write argument
    cams_arg: str = "--cams" if (with_cams) else ""

    # l2a_time_format format for dates
    fromdate = utils.to_str(fromdate, "%Y-%m-%d")
    todate = utils.to_str(todate, "%Y-%m-%d")

    # Check tile format and DTM
    utils.ensure_correct_tile_pattern(tile_id)

    # Output directory creation
    path_linkto = os.path.join(L2A_ROOT, site, f"{tile_id}")
    if run:
        os.makedirs(path_linkto, exist_ok=True)

    # Creation input folder for maja
    path_folders_file: str = build_maja_input_folder(
        maja_version, noenv, nocir
    )
    maja_id: str = maja_version_to_str(maja_version, noenv, nocir)

    # Format shell script for sbatch
    job_name = f"maja_{site}_{tile_id}_{fromdate}_{todate}"

    sbatch_content = slurm_maja.format(
        job_name=job_name,
        TMP_DIR=utils.TMP_PATH,
        path_folders_file=path_folders_file,
        tile_id=tile_id,
        site=site,
        fromdate=fromdate,
        todate=todate,
        maja_version=maja_version,
        CONF_ROOT=CONF_ROOT,
        maja_id=maja_id,
        cams_arg=cams_arg,
        path_linkto=path_linkto,
    )

    # Create shell script for sbatch
    script_path = os.path.join(utils.TMP_PATH, f"{job_name}.sh")
    with open(script_path, "w") as f:
        f.write(sbatch_content)
    os.chmod(script_path, 0o755)
    logger.info("SLURM script written: %s", script_path)

    # Eventually run Maja directly
    if run:
        logger.info("Submit SLURM job: %s", script_path)
        subprocess.run(["sbatch", script_path], check=True)
    else:
        logger.info("run=False -> job not submitted: %s", script_path)


def maja_version_to_str(
    maja_version: str,
    noenv: bool,
    nocir: bool,
) -> str:
    """Convert a MAJA software version to a str.

    Eventually adds a suffix for `noenv` or `nocir` modes.
    """
    maja_str: str = ""
    if maja_version == "4.8.0":
        maja_str = "480"
    elif maja_version == "4.8.1":
        maja_str = "481"
    elif maja_version == "4.9.3":
        maja_str = "393"
    elif maja_version == "4.10.0":
        maja_str = "410"
    else:
        raise ValueError("Maja version not handled.")
    if nocir:
        maja_str += "_nocir"
    if noenv:
        maja_str += "_noenv"
    return maja_str


def build_maja_input_folder(
    maja_version: str,
    noenv: bool,
    nocir: bool,
) -> str:
    """Build a folder.txt file necessary for the MAJA launching.

    The folder.txt file contains all the paths required by MAJA
    to work properly.
    """
    maja_id = maja_version_to_str(maja_version, noenv, nocir)

    file_content = maja_input_folders.format(
        maja_id=maja_id,
        maja_version=maja_version,
        L1C_ROOT=L1C_ROOT,
        L2A_ROOT=L2A_ROOT,
        DTM_ROOT=DTM_ROOT,
        CAMS_ROOT=CAMS_ROOT,
    )

    script_path = os.path.join(
        utils.TMP_PATH,
        f"maja_folders_{maja_id}.txt",
    )
    with open(script_path, "w") as f:
        f.write(file_content)
    os.chmod(script_path, 0o755)
    logger.info("SLURM script written: %s", script_path)

    return script_path
