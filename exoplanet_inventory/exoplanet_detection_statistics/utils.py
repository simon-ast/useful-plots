import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticks
import numpy as np
import pandas as pd
import polars as pl
import pyvo

# GLOBAL: COLOUR-WHEEL FOR BAR-CHART
COLOURMAP = [
        "tab:red", "tab:orange", "gold", "tab:green", "skyblue", "tab:blue",
        "mediumorchid", "violet", "fuchsia", "hotpink", "lightpink"
]


def cumulative_discovery_data(
        ascending_discovery_frame: pl.DataFrame
        ) -> dict:
    # Determine years counted for discoveries
    discovery_years = np.arange(
        ascending_discovery_frame["disc_year"].min(),
        ascending_discovery_frame["disc_year"].max() + 1
    )

    # List of discovery methods ('maintain_order' must be true to sort
    # methods by discovery year)
    discovery_methods = ascending_discovery_frame.unique(
        subset="discoverymethod", maintain_order=True
    )["discoverymethod"].to_numpy()

    # Create a dictionary of cumulative counts for each method
    cumulative_counts = method_dictionary(
        years=discovery_years, methods=discovery_methods,
        dataframe=ascending_discovery_frame
    )

    return cumulative_counts


def fill_discovery_plot(axis: plt.Axes, cumulative_data: dict) -> None:
    # Aux. variable: number of years to count
    year_count = cumulative_data["year"].shape[0]

    # Instantiate bar-bottom values to stack histogramme
    bar_bottom = np.zeros(year_count)

    # Make a dynamic colourmap
    num_methods = cumulative_data["method_names"].shape[0]
    cmap = mpl.colormaps["gist_rainbow"].resampled(num_methods)
    cmap = cmap(range(num_methods))

    # Plot all methods back-to-front
    for method_idx, method in enumerate(cumulative_data["method_names"][::-1]):

        axis.bar(
            cumulative_data["year"], cumulative_data[method],
            bottom=bar_bottom, label=method,
            # color=COLOURMAP[method_idx]
            color=cmap[method_idx]
        )

        # Update the bar-bottom values to stack histogramme
        bar_bottom += cumulative_data[method]

    # Reverse legend to show the earliest method at the top
    axis.legend(frameon=False, prop={'size': 8.5}, reverse=True)

    # Since the y-axis is logarithmic, small workaround to show a count of 1
    axis.set(ylim=(6e-1, 1e4))


def method_dictionary(
        years: np.ndarray[int],
        methods: np.ndarray[str],
        dataframe: pl.DataFrame
        ) -> dict:
    # Instantiate result dictionary with list of years
    result_dictionary = {"year": years, "method_names": methods}

    # Create keys for each method
    for method in methods:
        result_dictionary[method] = []

    # Loop over all counted years
    for year in years:
        subframe = dataframe.filter(pl.col("disc_year") <= year)

        # Loop over each method and append array-shape (= number of planets)
        for method in methods:
            method_frame = subframe.filter(pl.col("discoverymethod") == method)
            result_dictionary[method].append(method_frame.shape[0])

    # Make all listts into numpy arrays
    for method in methods:
        result_dictionary[method] = np.array(result_dictionary[method])

    return result_dictionary


def plot_spacemission_indicator(
        axis: plt.Axes,
        launch_year: int,
        linestyle: str,
        ) -> None:
    # Plot as vertical line
    axis.axvline(
        x=launch_year, c="k", ls=linestyle
    )

    return None


def read_exoplanet_parameters() -> pl.DataFrame:
    # Read epa file as polars data frame
    filename = "nasa_epa_fulldata.csv"
    exoplanet_data = pl.read_csv(filename)

    return exoplanet_data


def set_discovery_figure(space_missions: bool) -> tuple[plt.Figure, plt.Axes]:
    figure, axis = plt.subplots(figsize=(6, 5))

    # Axis formatting settings
    axis.set(
        xlabel="Discovery year",
        ylabel="Cumulative number of known exoplanets",
        yscale="log"
    )

    # Customise y-axis ticks and labels
    axis.set(
        yticks=[1, 10, 100, 1000, 10000],
        yticklabels=["1", "10", "100", "10$^3$", "10$^4$"]
    )

    # Potentially plot additional information
    if space_missions:
        mission_data = {
            "Kepler": 2009, "K2": 2014, "TESS": 2018
        }
        for _, year in mission_data.items():
            plot_spacemission_indicator(axis, year, "--")

    return figure, axis


def set_discovery_figure_alt(
        space_missions: bool
) -> tuple[plt.Figure, plt.Axes]:
    """DOC!"""
    figure, axis = plt.subplots(figsize=(10, 4), constrained_layout=True)

    axis.set(
        xlabel="Discovery year",
        # ylabel="Cumulative number of known exoplanets",
        ylabel="$\\Sigma$ of exoplanets",
        yscale="log"
    )

    return figure, axis


def update_exoplanet_parameters() -> None:
    # Set the NASA Exoplanet Archive as the TAP ressource
    tap_resource = "https://exoplanetarchive.ipac.caltech.edu/TAP"
    tap_service = pyvo.dal.TAPService(tap_resource)

    # Convert search result immediately to pandas DataFrame
    search_result = pd.DataFrame(
        tap_service.search(
            "SELECT pl_name, disc_year, discoverymethod, pl_rade, pl_orbper "
            "FROM ps "
            "WHERE default_flag = 1 "
            # "AND pl_controv_flag != 1"
        )
    )

    # Save a mark with current day for posterity
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    with open("marker_file.txt", "w") as marker_file:
        marker_file.write(
            f"Exoplanet data in 'nasa_epa_fulldata.csv' was queried on {today}"
        )

    # Save search result as csv-file
    search_result.to_csv("nasa_epa_fulldata.csv")

    return None
