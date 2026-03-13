"""
Format the CSV file with sample points from the GLORIA dataset.
"""

from pygeodes import Geodes

import insitudata_loader.utils as utils
import insitudata_loader.core as core


def main():
    data = core.GloriaInSituData(keep_nan=False)

    pipeline: utils.Pipeline = utils.Pipeline(
        core.TilesLocator(),
        core.FilterDate(datemin="2017-01-01", datemax="2025-01-01"),
        core.ComputeS2BandRrs(
            sat=["S2A", "S2B"],
            bands=["B1", "B2", "B3", "B4", "B5", "B6", "B7"],
        ),
        core.ComputeDayBounds(),
        core.PlotRrs(
            sat=["S2A", "S2B"],
            bands=["B1", "B3"],
            metadata=[
                "Distance_to_shore",
                "Cloud_fraction",
                "AOT",
            ],
        ),
        core.SaveToCsv("data/out/gloria_samples.csv"),
    )

    final_data = pipeline(data)
    print(final_data)

    print(len(final_data.df["tile"].unique()))
    tiles = final_data.df["tile"].unique()
    for tile in tiles:
        df_sel = final_data.df[final_data.df["tile"] == tile]
        print(df_sel["datemin"].min(), df_sel["datemin"].max())


if __name__ == "__main__":
    main()
