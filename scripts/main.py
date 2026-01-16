from insitudata_loader.utils import Pipeline, GeodesCollectionType
from insitudata_loader.core import (
    GloriaInSituData,
    TilesLocator,
    ComputeDayBounds,
    FilterDate,
    SearchOnGeodes,
)
from insitudata_loader.visu import visualize_item


def main():
    data = GloriaInSituData(keep_nan=False)

    pipeline: Pipeline = Pipeline(
        TilesLocator(),
        FilterDate(datemin="2021-01-01", datemax="2022-01-01"),
        ComputeDayBounds(),
        SearchOnGeodes(10.0, GeodesCollectionType.L2A),
        SearchOnGeodes(10.0, GeodesCollectionType.L1C),
        keep_intermediate_values=True,
    )

    final_data = pipeline(data)

    for _, row in final_data.df.iterrows():
        item_l2a = getattr(row, "L2A")
        visualize_item(item_l2a)


if __name__ == "__main__":
    main()
