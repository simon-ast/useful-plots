import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import pyvo


def main():
    # Auxiliary: Read Solar System data sheet
    solarsystem: pl.DataFrame = pl.read_csv("solar_system.csv")

    # Self-compiled: Read information for JWST C1 - C3
    namestring = ""

    for i in range(1, 4):
        query = pl.read_csv(f"JWST_targets_c{i}.csv")

        # Possible: Filter by specific parameters
        # query = query.filter(pl.col("Type") == "Eclipse")

        for element in query["Target Name"].to_numpy():
            namestring += f"'{element}',"

    # Remove the last, redundant "," in 'namestring'
    namestring = np.array(namestring[:-1])

    # Exoplanet Archive as TAP query source
    tap_source = "https://exoplanetarchive.ipac.caltech.edu/TAP"
    service = pyvo.dal.TAPService(tap_source)

    # Targets of JWST C1, C2, C3
    query_jwst = ("SELECT pl_name, pl_rade, pl_orbper, pl_eqt FROM pscomppars"
                  f"WHERE pl_name in ({namestring})")
    jwst_table = service.search(query_jwst)

    # Inventory of known exoplanets
    full_query = ("SELECT pl_name, pl_rade, pl_orbper, pl_eqt FROM ps WHERE "
                  "default_flag = 1")
    full_table = service.search(full_query)

    # Extract WASP-39 b from query
    w39b_idx = np.where(jwst_table["pl_name"] == "WASP-39 b")[0]

    # Make homogeneous plot limits from JWST targets and Solar System data
    xlims, ylims = make_plot_limits(
        jwst_targets=jwst_table, solar_system_data=solarsystem
    )

    # ITERATIVE PLOTS (I MUST BE ABLE TO AUTOMATE THIS!?)
    # Solar System only
    fig, ax = exoplanet_pop_figure_set()
    ax = plot_solar_system(axis=ax, solar_system=solarsystem)
    ax.set(xlim=xlims, ylim=ylims)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig("exoplanets_solarsystem.png", dpi=600)
    plt.close(fig)

    # Solar System + known exoplanets
    fig, ax = exoplanet_pop_figure_set()
    ax = plot_all_exoplanets(axis=ax, all_planets_table=full_table)
    ax = plot_solar_system(axis=ax, solar_system=solarsystem)
    ax.set(xlim=xlims, ylim=ylims)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig("exoplanets_solarsystem+all.png", dpi=600)
    plt.close(fig)

    # Solar System + known exoplanets + JWST targets + WASP-39
    fig, ax = exoplanet_pop_figure_set()
    ax = plot_jwst_targets(axis=ax, jwst_targets=jwst_table)
    ax = plot_all_exoplanets(axis=ax, all_planets_table=full_table)
    ax = plot_solar_system(axis=ax, solar_system=solarsystem)
    ax.set(xlim=xlims, ylim=ylims)
    ax.legend(loc="lower right")
    fig.tight_layout()
    plt.savefig("exoplanets_solarsystem+all+jwst.png", dpi=600)
    plt.close(fig)

    # Solar System + known exoplanets + JWST targets + WASP-39
    fig, ax = exoplanet_pop_figure_set()
    ax = plot_wasp39b(
        axis=ax, jwst_target_data=jwst_table, planet_idx=w39b_idx
    )
    ax = plot_jwst_targets(axis=ax, jwst_targets=jwst_table)
    ax = plot_all_exoplanets(axis=ax, all_planets_table=full_table)
    ax = plot_solar_system(axis=ax, solar_system=solarsystem)
    ax.set(xlim=xlims, ylim=ylims)
    ax.legend(loc="lower right")
    fig.tight_layout()
    plt.savefig("exoplanets_solarsystem+all+jwst+w39b.png", dpi=600)
    plt.close(fig)

    return None


def exoplanet_pop_figure_set() -> tuple[plt.Figure, plt.Axes]:
    figure, axis = plt.subplots(figsize=(6, 5))

    # Preliminary information
    axis.set(
        xscale="log", yscale="log",
        xlabel="$P$ [d]", ylabel="$R_\\mathrm{p}$ [$\\mathrm{R}_\\oplus$]"
    )

    # Make background outside plot-square transparent
    figure.patch.set_facecolor('none')

    return figure, axis


def make_plot_limits(
        jwst_targets: pl.DataFrame,
        solar_system_data: pl.DataFrame
        ) -> tuple:
    temporary_figure, temporary_axis = exoplanet_pop_figure_set()

    axis = plot_jwst_targets(axis=temporary_axis, jwst_targets=jwst_targets)
    axis = plot_solar_system(
        axis=temporary_axis, solar_system=solar_system_data
        )
    axis.set(yscale="log", xscale="log")

    xaxis_limits, yaxis_limits = axis.get_xlim(), axis.get_ylim()

    # Close plot instance
    plt.close(temporary_figure)

    return xaxis_limits, yaxis_limits


def plot_all_exoplanets(
        axis: plt.Axes,
        all_planets_table: pl.DataFrame
        ) -> plt.Axes:

    axis.scatter(
        all_planets_table["pl_orbper"], all_planets_table["pl_rade"],
        c="grey", alpha=0.2, zorder=102, label="Known Exop."
    )

    return axis


def plot_jwst_targets(
        axis: plt.Axes,
        jwst_targets: pl.DataFrame
        ) -> plt.Axes:

    axis.scatter(
        jwst_targets["pl_orbper"], jwst_targets["pl_rade"],
        marker="+", zorder=103, label="JWST targets"
    )

    return axis


def plot_solar_system(
        axis: plt.Axes,
        solar_system: pl.DataFrame
        ) -> plt.Axes:

    axis.scatter(
        solar_system["porb"] * 365, solar_system["re"],
        c="k", label="Solar System", zorder=101
    )

    return axis


def plot_wasp39b(
        axis: plt.Axes,
        jwst_target_data: pl.DataFrame,
        planet_idx: int
        ) -> plt.Axes:

    axis.scatter(
        jwst_target_data["pl_orbper"][planet_idx],
        jwst_target_data["pl_rade"][planet_idx],
        marker="x", c="tab:red", zorder=104, label="WASP-39 b"
    )

    return axis


if __name__ == "__main__":
    plt.style.use(
        "https://raw.githubusercontent.com/simon-ast/"
        "matplotlib-plot-style/main/default_style.mplstyle"
        )
    main()
