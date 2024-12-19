import argparse
import polars as pl

import util


def main():
    arguments = argument_parser()

    # Check if EPA data should be updated
    if arguments.update:
        util.update_exoplanet_parameters()

    # Read EPA data
    epa_data = util.read_exoplanet_parameters()

    # Make the figure
    fig, ax = util.set_multifigure()
    
    # Take care of period-radius plot
    pr_constr = epa_data.filter(
        (pl.col("pl_orbper") < 1e3) & (pl.col("pl_rade") > 0.)
    )
    util.fill_axis(
        ax[0], pr_constr["pl_orbper"], pr_constr["pl_rade"],
        label_x="$P$ [d]", label_y="$R_\\mathrm{p}$ [R$_\\oplus$]",
        alpha=0.2
    )
    
    # Take care of period-mass plot
    pm_constr = epa_data.filter(
        (pl.col("pl_orbper") < 1e6) & (pl.col("pl_masse") > 1e-1)
    )
    util.fill_axis(
        ax[-1], pm_constr["pl_orbper"], pm_constr["pl_masse"],
        label_x="$P$ [d]", label_y="$M_\\mathrm{p}$ [M$_\\oplus$]",
        alpha=0.2
    )

    #util.clean_multifigure(fig, ax)
    fig.tight_layout()
    fig.savefig("first_test.png")


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
    main()
