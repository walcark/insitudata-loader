"""
Format the CSV file with sample points from the GLORIA dataset.
"""

from insitudata_loader.core import Pipeline
from insitudata_loader.sources.gloria import GloriaAdapter
from insitudata_loader.satellites import SRF
from insitudata_loader.satellites.sentinel2 import SearchOnGeodes
from insitudata_loader.transforms import (
    TilesLocator,
    FilterDate,
    ComputeDayBounds,
    ConvolveToSatelliteBands,
    PlotRrs,
    SaveToCsv,
)
from insitudata_loader.utils import S2_SRF_PATH, S2_TILES_PATH


def main():
    data = GloriaAdapter(keep_nan=False).load()

    pipeline = Pipeline(
        TilesLocator(S2_TILES_PATH),
        FilterDate(datemin="2017-01-01", datemax="2025-01-01"),
        ConvolveToSatelliteBands(
            srf=SRF(S2_SRF_PATH),
            sat=["S2A", "S2B"],
            bands=["B1", "B2", "B3", "B4", "B5", "B6", "B7"],
        ),
        ComputeDayBounds(),
        PlotRrs(
            sat=["S2A", "S2B"],
            bands=["B1", "B3"],
            metadata=[
                "Distance_to_shore",
                "Cloud_fraction",
                "AOT",
            ],
        ),
        SaveToCsv("data/out/gloria_samples.csv"),
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
