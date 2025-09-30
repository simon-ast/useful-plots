import matplotlib as mpl
import matplotlib.patches as patch
import matplotlib.figure as m_fig
import matplotlib.axes as m_ax
import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np


def projected_offset(adjacent: float, angle: float) -> float:
    """DOC!"""
    return adjacent / np.cos(angle)


def make_line(
        k_value: float, offset: float, angle: float,
        x_array: np.ndarray
        ) -> np.ndarray:
    """DOC!"""
    return k_value * x_array + projected_offset(offset, angle)


def transit_cord_auxilary(
        x_array: np.ndarray,
        planet_size: float,
        impact_param: float,
        proj_obliquity: float,
        ) -> list:
    """
    DOC!

    :param planet_size:     Size of the planet in stellar radii
    :param impact_param:    Impact parameter
    :param proj_obliquity:  Projected obliquity angle of planet orbit [deg]
    """

    # Note: The "inclination angle" here seems to be something that,
    # effectively, can only be measured through the Rossiter-McLaughlin
    # effect?

    # This implies that I don't really need this function at the moment,
    # and could use the ax_hspan() function to make a horinzotally filled
    # area, but I might as well keep this in and use it in the future in
    # some way

    # Transform obliquity from degrees into radians
    proj_obliquity *= np.pi / 180

    # Values of the planet centre and edges at mid-transit
    planet_centre: float = impact_param
    upper_edge: float = planet_centre + planet_size
    lower_edge: float = planet_centre - planet_size

    # Linear inclination
    inclination_absolute: float = np.tan(proj_obliquity)

    # Make arrays for all three cord lines
    """centre_line = make_line(
        inclination_absolute, planet_centre, proj_obliquity, x_array
    )
    top_line = make_line(
        inclination_absolute, upper_edge, proj_obliquity, x_array
    )
    bottom_line = make_line(
        inclination_absolute, lower_edge, proj_obliquity, x_array
    )"""
    return_list = [
        make_line(
            inclination_absolute, location, proj_obliquity, x_array
        ) for location in [planet_centre, upper_edge, lower_edge]
    ]

    return return_list


def draw_canvas() -> tuple[m_fig.Figure, m_ax.Axes]:
    # General
    figure, axis = plt.subplots()

    # Canvas shape
    axis.set(xlim=(-1.5, 1.5), ylim=(-1.5, 1.5), xticks=[], yticks=[])
    axis.set_aspect("equal")
    figure.patch.set_facecolor('none')

    return figure, axis


def draw_sketch(planet_parameters: dict) -> m_fig.Figure:
    """Wrapper for makin the sketch"""
    # Backdrop
    fig, ax = draw_canvas()

    # Stellar disk
    draw_star(ax, planet_parameters["st_teff"])

    # Draw transit cord
    x_array = np.linspace(-1.5, 1.5, 100)
    centre, top, bottom = transit_cord_auxilary(
        x_array, planet_parameters["ratio_rtor"],
        planet_parameters["impact_par"], planet_parameters["pl_projobliq"]
    )
    draw_transit_cord(ax, x_array, centre, top, bottom)

    # Final clean-up
    fig.tight_layout()

    return fig


def draw_star(axis: m_ax.Axes, star_teff: float) -> None:
    """
    Draws a circle of radius 1 on the axis-object.
    In this reference frame, the stellar radius will always be 1!
    """
    plot_colour = stellar_temp_cmap(star_teff)
    stellar_disk = patch.Circle(
        (0, 0), radius=1., color=plot_colour
    )
    axis.add_patch(stellar_disk)

    return None


def stellar_temp_cmap(temperature: float) -> np.ndarray:
    """Map stellar host temperature to RGBA value of colormap."""
    norm = colors.Normalize(vmin=1000, vmax=10000)
    cmap = mpl.colormaps["YlOrRd_r"]

    mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
    colour = mappable.to_rgba(np.array([temperature]))

    return colour


def draw_transit_cord(
        axis: m_ax.Axes,
        x_array: np.ndarray,
        centre_line: np.ndarray,
        top_edge: np.ndarray,
        bottom_edge: np.ndarray
        ) -> None:
    """
    Draw the semi-transparent transit cord onto the axis-object.

    :param axis:        Axis-object to draw onto
    :param x_array:     Mappable x-array from axis
    :param centre_line: Array of transit centre line
    :param top_edge:    Array of transit top edge
    :param bottom_edge: Array of bottom edge

    :return:
        None, axis is altered in-place
    """
    # Planet transit centre line
    axis.plot(x_array, centre_line, c="k", ls="--")

    # Planet transit cord
    axis.fill_between(
        x=x_array, y1=top_edge, y2=bottom_edge, color="k", alpha=0.7
    )

    return None
