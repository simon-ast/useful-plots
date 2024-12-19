# Compare WASP-39 b data: Spitzer, HST, full JWST coverage

import polars as pl
import matplotlib.pyplot as plt

import util as u


def main():
    col_pre = wrap_collected_spectra("pre-JWST")
    col_post = wrap_collected_spectra("post-JWST")

    fig, ax = plt.subplots()
    plot_separated(col_pre, ax)
    plot_together(col_post, ax)
    ax.legend()

    plt.show()


def wrap_collected_spectra(folder):
    information = pl.read_csv(
        f"{folder}/spectra.csv", truncate_ragged_lines=True
    )

    collection = []
    for idx in range(information.shape[0]):
        temp_data = information.row(idx, named=True)
        name = temp_data["SPEC_PATH"].split("/")[-1]
        ref = temp_data["AUTHORS"]

        try:
            collection.append(
                u.SpectralData(f"{folder}/{name}", reference=ref)
            )
        except FileNotFoundError:
            print(f"FILE {name} NOT FOUND\n")

    return collection


def plot_separated(collection, axis):
    for spectrum in collection:
        axis.errorbar(
            spectrum.lam_cen, spectrum.td,
            xerr=spectrum.lam_err,
            yerr=[spectrum.td_err_pos, spectrum.td_err_neg],
            ms=4, fmt="o", label=spectrum.ref
        )

    return None


def plot_together(collection, axis):
    spectrum = collection[0]
    axis.errorbar(
        spectrum.lam_cen, spectrum.td,
        xerr=spectrum.lam_err,
        yerr=[spectrum.td_err_pos, spectrum.td_err_neg],
        ms=4, fmt="o", label=spectrum.ref, c="k"
    )

    for spectrum in collection[1:]:
        axis.errorbar(
            spectrum.lam_cen, spectrum.td,
            xerr=spectrum.lam_err,
            yerr=[spectrum.td_err_pos, spectrum.td_err_neg],
            ms=4, fmt="o", c="k"
        )

    return None


if __name__ == "__main__":
    main()
