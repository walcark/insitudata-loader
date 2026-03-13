import matplotlib.pyplot as plt

from pygeodes import Geodes

from insitudata_loader.utils import (
    Pipeline,
    GeodesCollectionType,
    get_pygeodes_config,
)
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

    if False:
        fig, ax = plt.subplots(figsize=(6.8, 4.8))
        data.df["Rrs_mean_492"].plot(ax=ax, label="Rrs_mean_492")
        data.df["Rrs_mean_560"].plot(ax=ax, label="Rrs_mean_560")
        data.df["Rrs_mean_865"].plot(ax=ax, label="Rrs_mean_865")
        ax.legend()
        print(data.df)
        plt.show()

    pipeline: Pipeline = Pipeline(
        TilesLocator(),
        FilterDate(datemin="2017-01-01", datemax="2023-01-01"),
        ComputeDayBounds(),
        SearchOnGeodes(50.0, GeodesCollectionType.L1C),
        keep_intermediate_values=True,
    )

    pipeline2: Pipeline = Pipeline(
        TilesLocator(),
        FilterDate(datemin="2017-01-01", datemax="2023-01-01"),
        ComputeDayBounds(),
    )

    final_data = pipeline2(data)

    final_data.save("file.csv")

    items = []
    for _, row in final_data.df.iterrows():
        item_l1c = getattr(row, "L1C")
        items.append(item_l1c)
        try:
            Geodes(conf=get_pygeodes_config()).download_item_archive(
                item_l1c
            )
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
