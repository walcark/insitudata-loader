"""
l1c.py

Author  : Kévin Walcarius
Date    : 2026-03-13
Version : 1.0
License : MIT
Summary : Command to launch the extraction of L1C files with Amalthee.
"""

import subprocess
import os

import insitudata_loader.utils as utils
from .paths import L1C_ROOT, TREX_EXT_ROOT
from .slurm_commands import slurm_l1c

logger = utils.get_logger(__name__)


def build_slurm_to_download_l1c(
    site: str,
    tile_id: str,
    fromdate: str,
    todate: str,
    mail: str = "kevin.walcarius@cnes.fr",
    n_cpu: int = 1,
    run: bool = False,
) -> tuple[list[str], list[str]]:
    """Create and save SLURM submit scripts to download L1C files.

    Eventually launch the SLURM files directly if required.

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
    mail (str):
        Email address to receive SLURM notifications.
    n_cpu (int):
        Number of sub-jobs (time segments) to create.
    run (bool):
        If True, submit each generated script with `sbatch`.

    Returns
    -------
    tuple[list[str], list[str]]:
        A tuple of two lists:
        - The first list contains the paths to the generated SLURM scripts.
        - The second list contains the corresponding output directory paths.
    """
    # Output directory creation
    path_linkto = os.path.join(L1C_ROOT, site, f"T{tile_id}")
    if run:
        os.makedirs(path_linkto, exist_ok=True)

    # Create multiple-periods for the number of cpus
    tranches = utils.create_periods_for_cpu(fromdate, todate, n_cpu)

    # Iterates over the periods ans format shell scripts for sbatch
    script_paths, out_paths = [], []
    for idx, (t0, t1) in enumerate(tranches, start=1):
        sub_from = utils.to_str(t0, "%Y-%m-%d")
        sub_to = utils.to_str(t1, "%Y-%m-%d")
        job_name = f"get{site}_{tile_id}_{sub_from}_{sub_to}_part{idx}"

        sbatch_content = slurm_l1c.format(
            job_name=job_name,
            TMP_DIR=utils.TMP_PATH,
            TREX_EXT_ROOT=TREX_EXT_ROOT,
            tile_id=tile_id,
            sub_from=sub_from,
            sub_to=sub_to,
            path_linkto=path_linkto,
            mail=mail,
        )

        # Create shell script for sbatch
        script_path = os.path.join(utils.TMP_PATH, f"{job_name}.sh")
        with open(script_path, "w") as f:
            f.write(sbatch_content)
        os.chmod(script_path, 0o755)
        logger.info("SLURM script written: %s", script_path)

        # Eventually run Amalthee directly
        if run:
            logger.info("Submit SLURM job: %s", script_path)
            subprocess.run(["sbatch", script_path], check=True)
        else:
            logger.info("run=False -> job not submitted: %s", script_path)

        script_paths.append(script_path)
        out_paths.append(path_linkto)

    return (script_paths, out_paths)
