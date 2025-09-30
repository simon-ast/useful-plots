import argparse
import polars as pl

import util


COLOURMAP = [
        "tab:red", "tab:orange", "gold", "tab:green", "skyblue", "tab:blue",
        "mediumorchid", "violet", "fuchsia", "hotpink", "lightpink"
]


def main():
    arguments = argument_parser()

    # Check if EPA data should be updated
    if arguments.update:
        util.update_exoplanet_parameters()

    # Read EPA data
    epa_data, sorting = util.read_exoplanet_parameters()

    # Make the figure
    fig, ax = util.set_multifigure()

    # Take care of period-radius plot
    pr_constr = epa_data.filter(
        (pl.col("pl_orbper") < 1e6) &
        (pl.col("pl_rade") > 0.)
    )
    for idx, element in enumerate(sorting.keys()):
        alpha = 0.5
        pr_select = pr_constr.filter(pl.col("discoverymethod") == element)

        if pr_select.shape[0] > 1000:
            alpha = 0.2

        util.fill_axis(
            ax[0], pr_select["pl_orbper"], pr_select["pl_rade"],
            alpha=alpha, color=COLOURMAP[idx]
        )
        ax[0].set(xlabel="$P$ [d]", ylabel="$R_\\mathrm{p}$ [R$_\\oplus$]")

    # Take care of period-mass plot
    pm_constr = epa_data.filter(
        (pl.col("pl_orbper") < 1e6) &
        (pl.col("pl_masse") > 1e-1)
    )
    for idx, element in enumerate(sorting.keys()):
        pm_select = pm_constr.filter(pl.col("discoverymethod") == element)
        alpha = .5

        if pm_select.shape[0] > 1000:
            alpha = .2

        util.fill_axis(
            ax[-1], pm_select["pl_orbper"], pm_select["pl_masse"],
            alpha=alpha, color=COLOURMAP[idx]
        )
    ax[1].set(xlabel="$P$ [d]", ylabel="$M_\\mathrm{p}$ [M$_\\oplus$]")

    fig.savefig("period-radius_period-mass.pdf")


def argument_parser() -> argparse.Namespace:
    # Instantiate argument parser
    parser = argparse.ArgumentParser(
        prog="Cumulative exoplanet statistics",
        description="""
            Small script that generates some exoplanet statistics,
            and optionally includes markers for significant
            space missions.
        """,
    )

    # Add boolean update argument
    parser.add_argument(
        "-u", "--update",
        action=argparse.BooleanOptionalAction
    )

    # Add boolean "space mission" argument
    parser.add_argument(
        "-sm", "--spacemissions",
        action=argparse.BooleanOptionalAction
    )

    return parser.parse_args()


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    plt.style.use(
        "https://raw.githubusercontent.com/simon-ast/matplotlib-plot-style/"
        "main/corner_style.mplstyle"
    )
    main()
