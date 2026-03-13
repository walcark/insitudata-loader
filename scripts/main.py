from pygeodes import Geodes

from insitudata_loader.core import Pipeline
from insitudata_loader.sources.gloria import GloriaAdapter
from insitudata_loader.satellites import GeodesCollectionType, get_pygeodes_config, SearchOnGeodes, Satellite
from insitudata_loader.transforms import TilesLocator, FilterDate, ComputeDayBounds
from insitudata_loader.visu import visualize_item


def main():
    data = GloriaAdapter(keep_nan=False).load()

    pipeline = Pipeline(
        TilesLocator(Satellite.SENTINEL2),
        FilterDate(datemin="2017-01-01", datemax="2023-01-01"),
        ComputeDayBounds(),
        SearchOnGeodes(50.0, GeodesCollectionType.S2_L1C),
        keep_intermediate_values=True,
    )

    pipeline2 = Pipeline(
        TilesLocator(Satellite.SENTINEL2),
        FilterDate(datemin="2017-01-01", datemax="2023-01-01"),
        ComputeDayBounds(),
    )

    final_data = pipeline2(data)

    final_data.save("file.csv")

    items = []
    for _, row in final_data.df.iterrows():
        item_l1c = getattr(row, "S2_L1C")
        items.append(item_l1c)
        try:
            Geodes(conf=get_pygeodes_config()).download_item_archive(item_l1c)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
