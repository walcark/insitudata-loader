"""
Launch the extraction of Sentinel-2 L1C files for GLORIA measurement points.
"""

import argparse

from insitudata_loader.sources.gloria import GloriaAdapter
from insitudata_loader.core import Pipeline
import insitudata_loader.satellites as sat
import insitudata_loader.transforms as transforms
import insitudata_loader.maja as maja
from insitudata_loader.utils import get_logger

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Schedule Sentinel-2 L1C downloads for GLORIA data points."
    )
    parser.add_argument(
        "site",
        help="Experience name attached to the MAJA run (e.g. val_adjeff).",
    )
    parser.add_argument(
        "--datemin",
        default="2017-01-01",
        metavar="YYYY-MM-DD",
        help="Start date filter (default: 2017-01-01).",
    )
    parser.add_argument(
        "--datemax",
        default="2025-01-01",
        metavar="YYYY-MM-DD",
        help="End date filter (default: 2025-01-01).",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Submit SLURM jobs immediately (default: dry-run only).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    logger.info("Loading GLORIA dataset.")
    data = GloriaAdapter(keep_nan=False).load()

    pipeline = Pipeline(
        transforms.TilesLocator(sat.Satellite.SENTINEL2),
        transforms.FilterDate(datemin=args.datemin, datemax=args.datemax),
        transforms.ConvolveToSatelliteBands(
            srf=sat.SRF(sat.Satellite.SENTINEL2),
            sat=["S2A", "S2B"],
            bands=["B1", "B2", "B3", "B4", "B5", "B6", "B7"],
        ),
        transforms.ComputeDayBounds(),
        transforms.SaveToCsv("data/out/gloria_samples.csv"),
    )

    logger.info("Running pipeline (datemin=%s, datemax=%s).", args.datemin, args.datemax)
    final_data = pipeline(data)

    entries = maja.schedule_maja(final_data, name=args.site)
    logger.info("Scheduling %d SLURM jobs for site '%s'.", len(entries), args.site)
    for entry in entries:
        maja.build_slurm_to_download_l1c(run=args.run, **entry)


if __name__ == "__main__":
    main()
