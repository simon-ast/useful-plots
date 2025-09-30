import argparse

import utils as u


def main() -> None:
    # Argument parser
    args = argument_parser()

    # Update data file only if requested
    if args.update:
        u.update_exoplanet_parameters()

    # Instantiate the plotting frame(s)
    fig, ax = u.set_discovery_figure(space_missions=args.spacemissions)

    # Generate main data frame, sorted by discovery year
    exoplanet_discoveries = u.read_exoplanet_parameters().sort(by="disc_year")

    # Generate cumulative discovery list, sorted by discovery method
    cumulative_discoveries = u.cumulative_discovery_data(exoplanet_discoveries)

    # Fill in the discovery plot and save figure
    u.fill_discovery_plot(axis=ax, cumulative_data=cumulative_discoveries)
    fig.tight_layout()
    fig.savefig("cumulative_exoplanet_discoveries.svg")
    fig.savefig("cumulative_exoplanet_discoveries.pdf")

    # Do this (quick and dirty) for alternative figure as well
    import matplotlib.pyplot as plt
    fig_alt, ax_alt = u.set_discovery_figure_alt(
        space_missions=args.spacemissions
    )

    import numpy as np
    years = cumulative_discoveries["year"]
    total = np.zeros(years.shape[0])

    for key, item in cumulative_discoveries.items():
        if key in ["year", "method_names"]:
            pass
        else:
            total = np.add(total, item)
            idxs = np.where(item > 0)
            ax_alt.plot(years[idxs], item[idxs], label=key, ls="-", lw=1.5)

    ax_alt.plot(years, total, c="k", lw=3, zorder=0)
    ax_alt.set(
        yticks=[1, 10, 100, 1000, 10000],
        yticklabels=["1", "10", "100", "10$^3$", "10$^4$"]
    )
    ax_alt.legend()

    fig_alt.savefig("individual_exoplanet_discoveries.pdf")


def argument_parser() -> argparse.ArgumentParser:
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
