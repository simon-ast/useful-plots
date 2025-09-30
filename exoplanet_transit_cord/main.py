import argparse

import modules.get_data as data
import modules.make_plot as plotting


def main() -> None:
    parser = argument_parser()

    planet_data = data.get_parameters(planet_name=parser.name)

    figure = plotting.draw_sketch(planet_data)

    figure.savefig("exoplanet_transit_cord.png", dpi=600)

    return None


def argument_parser() -> argparse.Namespace:
    # Instantiate argument parser
    argument_parser = argparse.ArgumentParser(
        prog="Generate exoplanet transit cord sketch",
        description="""
        Name of exoplanet will query the exoplanet archive for necessary
        system parameters and draw a transit cord sketch.
        """,
    )

    # Read planet name as command line argument
    argument_parser.add_argument(
        "-n", "--name", required=True,
        help="name of exoplanet to send to NASA EPA"
        )

    return argument_parser.parse_args()


if __name__ == "__main__":
    main()
