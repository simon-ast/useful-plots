import numpy as np


def calculate_impact_parameter(
        semimajor_axis: float,
        orbit_inclination: float,
        eccentricity: float,
        argument_periapsis: float
        ) -> float:
    """
    Calculation of orbital projected impact parameter, following equation (7)
    from Winn (2010). The calculation is split into the spherical part, as
    well as the addition of the correction for eccentric orbits.

    :param semimajor_axis:      Semi-major axis in units of stellar radius
    :param orbit_inclination:   Inclination of orbital plane in degrees
    :param eccentricity:        Orbital eccentricty
    :param argument_periapsis:  Argument of periapsis in degrees

    :return:
        Impact parameter of projected orbit
    """
    circular_part: float = (
        semimajor_axis * np.cos(orbit_inclination * np.pi / 180)
    )
    eccentric_addition: float = (
        (1 - eccentricity ** 2) /
        (1 + eccentricity * np.sin(argument_periapsis * np.pi / 180))
    )
    transit_impact_par: float = circular_part * eccentric_addition

    # Make a sanity check to ensure that the planet is actually transiting
    assert abs(transit_impact_par) <= 1.5, (
        f"Impact parameter {transit_impact_par} not possible to plot!"
    )

    return transit_impact_par
