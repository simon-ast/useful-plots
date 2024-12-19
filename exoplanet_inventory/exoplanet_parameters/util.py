import datetime
import matplotlib.pyplot as plt
import pandas as pd
import polars as pl
import pyvo


def set_multifigure():
    figure, total_axis = plt.subplots(
        figsize=(8, 4), ncols=2, #width_ratios=[4, 1, 4]
    )
    for axis in total_axis:
        axis.set(yscale="log", xscale="log")

    return figure, total_axis


def fill_axis(
    axis: plt.Axes,
    x_array: pd.Series,
    y_array: pd.Series,
    label_x: str,
    label_y: str,
    **kwargs
    ) -> None:
    """Generic string to fill an axis"""
    axis.scatter(x_array, y_array, **kwargs)
    axis.set(xlabel=label_x, ylabel=label_y)
    
    return None


def clean_multifigure(total_figure, total_axis):
    total_figure.tight_layout()
    total_axis[1].axis("off")


def read_exoplanet_parameters() -> pl.DataFrame:
    # Read epa file as polars data frame
    filename = "nasa_epa_fulldata.csv"
    exoplanet_data = pl.read_csv(filename)

    return exoplanet_data


def update_exoplanet_parameters() -> None:
    # Set the NASA Exoplanet Archive as the TAP ressource
    tap_resource = "https://exoplanetarchive.ipac.caltech.edu/TAP"
    tap_service = pyvo.dal.TAPService(tap_resource)

    # Convert search result immediately to pandas DataFrame
    search_result = pd.DataFrame(
        tap_service.search(
            "SELECT pl_name, pl_rade, pl_orbper, pl_masse, discoverymethod "
            "FROM ps "
            "WHERE default_flag = 1"  # type: ignore
        )
    )

    # Save a mark with current day for posterity
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    with open("marker_file.txt", "w") as marker_file:
        marker_file.write(
            "Exoplanet data in 'nasa_epa_fulldata.csv' "
            f"was queried on {today}"
        )

    # Save search result as csv-file
    search_result.to_csv("nasa_epa_fulldata.csv")

    return None
