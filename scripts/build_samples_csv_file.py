"""
Format the CSV file with sample points from the GLORIA dataset.
"""

from insitudata_loader.core import Pipeline
from insitudata_loader.sources.gloria import GloriaAdapter
from insitudata_loader.satellites import SRF, Satellite
from insitudata_loader.transforms import (
    TilesLocator,
    FilterDate,
    ComputeDayBounds,
    ConvolveToSatelliteBands,
    PlotRrs,
    SaveToCsv,
)
from insitudata_loader.maja import schedule_maja


def main():
    data = GloriaAdapter(keep_nan=False).load()

    pipeline = Pipeline(
        TilesLocator(Satellite.SENTINEL2),
        FilterDate(datemin="2017-01-01", datemax="2025-01-01"),
        ConvolveToSatelliteBands(
            srf=SRF(Satellite.SENTINEL2),
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

    tiles = final_data.df["tile"].unique()
    for tile in tiles:
        df_sel = final_data.df[final_data.df["tile"] == tile]
        print(df_sel["datemin"].min(), df_sel["datemin"].max())

    entries = schedule_maja(final_data, name="val_adjeff")
    for idx, entry in enumerate(entries):
        print(idx, entry)


if __name__ == "__main__":
    main()
