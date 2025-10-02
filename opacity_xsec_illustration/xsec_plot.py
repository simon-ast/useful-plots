import pandas as pd
import matplotlib.pyplot as plt


def main():
    h2o = read_xsec("H2O")
    co2 = read_xsec("CO2")
    ch4 = read_xsec("CH4")
    nh3 = read_xsec("NH3")
    so2 = read_xsec("SO2")

    fig, ax = make_figure(2, 3)
    for idx, element in enumerate([h2o, ch4, co2, nh3, so2]):
        fill_subplots(idx, ax, element)

    fig.supxlabel("$\\lambda$ [m]")
    fig.supylabel("$\\sigma$ [molecule$^{-1}$]")
    plt.show()


def read_xsec(filename: str) -> dict:
    data = pd.read_csv(
        f"binned_data/xsec_{filename}.csv",
        comment="#"
    )
    name = make_latex_string(filename)
    return_dict = {"id": filename, "name": name, "xsec": data}

    return return_dict


def make_latex_string(string: str) -> str:
    """Make e.g. H2O into H$_2$O"""
    new_string = ""

    for element in string:
        try:
            new_string += f"$_{int(element)}$"
        except ValueError:
            new_string += element

    return new_string


def make_figure(ncols: int, nrows: int):
    figure, axis = plt.subplots(
        ncols=ncols, nrows=nrows, figsize=(5*ncols, 3*nrows)
    )

    return figure, axis


def fill_subplots(plot_id: int, axis, data: dict):
    ax = axis.flatten()[plot_id]
    ax.plot(
        data["xsec"]["wavel [m]"], data["xsec"]["x-sec"],
        label=data["name"]
    )
    ax.set(xlim=(0.8e-6, 12e-6), yscale="log", xscale="log")
    ax.legend(loc="upper left")


if __name__ == "__main__":
    main()
