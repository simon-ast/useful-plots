import astropy.io.ascii as ascii
import polars as pl
import matplotlib.pyplot as plt


class SpectralData:
    """Read individual spectral data from the EPA (as IPAC tables)"""
    def __init__(self, filename: str, reference: str) -> None:
        self.ref = reference

        # Of course, give me an IPAC table, I've certainly used that before
        full_data = pl.DataFrame(ascii.read(filename).to_pandas())

        # Extract useful parameters
        self.lam_cen = full_data["CENTRALWAVELNG"].to_numpy()
        self.lam_err = full_data["BANDWIDTH"].to_numpy() / 2
        self.td = full_data["PL_TRANDEP"].to_numpy()
        self.td_err_pos = full_data["PL_TRANDEPERR1"].to_numpy()
        self.td_err_neg = full_data["PL_TRANDEPERR2"].to_numpy() * -1

    def __str__(self) -> str:
        return self.ref


def set_figure(size: tuple):
    figure, axis = plt.subplots(figsize=size)
    axis.set(
        xlabel="$\\lambda$ [$\\mu$m]",
        ylabel="($R_\\mathrm{p} / R_*$)$^2$ [%]"
    )
    
    return figure, axis


def plot_spectrum(
    axis: plt.Axes, spectrum: SpectralData,
    **kwargs
    ):
    
    axis.errorbar(
        spectrum.lam_cen, spectrum.td,
        xerr=spectrum.lam_err,
        yerr=[spectrum.td_err_pos, spectrum.td_err_neg],
        ms=4, fmt="o", **kwargs
    )
    
    return None

