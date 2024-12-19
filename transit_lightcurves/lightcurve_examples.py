import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BIN_SIZE = 50
plt.style.use("https://raw.githubusercontent.com/simon-ast/matplotlib-plot-style/main/default_style.mplstyle")

def box_median(array, binsize):
    median_array = []
    
    bin_start = 0
    bin_end = binsize
    number_array_elements = array.shape[0]
    
    while bin_end < number_array_elements - binsize:
        temporary_array = array[bin_start:bin_end]
        median_array.append(np.nanmedian(temporary_array))
    
        bin_start = bin_end
        bin_end += binsize
        
    median_array = np.array(median_array)
    
    return median_array


def plot_ready_data(filename, binsize=BIN_SIZE):
    
    lc_data = pd.read_csv(filename, comment="#", delim_whitespace=True)
    
    # X-axis
    time_bjmd = lc_data["time"]
    time_hrs = (time_bjmd - time_bjmd.iloc[0]) * 24
    binned_time = box_median(time_hrs, binsize)
    
    # Y-axis
    model = lc_data["transit"]
    binned_lc = box_median(1 + (lc_data["lcdata"] - lc_data["polynom"]), binsize)
    
    return {
        "time_hrs": time_hrs,
        "time_bin": binned_time,
        "lc_model": model,
        "lc_binned": binned_lc
    }


# White LC example
fig_white, ax_white = plt.subplots(figsize=(8, 4))
white_lc = plot_ready_data("w39b_lc_white.txt")

# Underlying data
ax_white.scatter(white_lc["time_bin"], white_lc["lc_binned"] * 1e2, alpha=0.5, c="grey", label="Data")

# Light-curve astrophysical model
ax_white.plot(white_lc["time_hrs"], white_lc["lc_model"] * 1e2, lw=2.5, c="k", label="Transit")

ax_white.legend()
ax_white.set(
    xlabel="Observed time [hrs]", ylabel="Normalised brightness [%]",
    xlim=(white_lc["time_hrs"].iloc[0], white_lc["time_hrs"].iloc[-1]),
    ylim=(0.974 * 1e2, 1.004 * 1e2)
)

fig_white.patch.set_facecolor('none')
fig_white.savefig(f"transit_example_whiteLC_bin{BIN_SIZE}.png", dpi=600)

#####################
# Spectroscopic example
fig_spec, ax_spec = plt.subplots(figsize=(8, 4))
binsize = 200
short_lc = plot_ready_data("w39b_lc_ch3.txt", binsize)
long_lc = plot_ready_data("w39b_lc_ch180.txt", binsize)

# Underlying data
ax_spec.scatter(long_lc["time_bin"], long_lc["lc_binned"] * 1e2, alpha=0.1, c="tab:red")
ax_spec.scatter(short_lc["time_bin"], short_lc["lc_binned"] * 1e2, alpha=0.1, c="tab:blue")


# Light-curve astrophysical model
ax_spec.plot(long_lc["time_hrs"], long_lc["lc_model"] * 1e2, lw=2.5, c="tab:red", label="Transit ($\\lambda \\approx 4.4 \, \\mu \\mathrm{m}$)")
ax_spec.plot(short_lc["time_hrs"], short_lc["lc_model"] * 1e2, lw=2.5, c="tab:blue", label="Transit ($\\lambda \\approx 2.2 \, \\mu \\mathrm{m}$)")

ax_spec.legend()
ax_spec.set(
    xlabel="Observed time [hrs]", 
    ylabel="Normalised brightness [%]",
    xlim=(short_lc["time_hrs"].iloc[0], short_lc["time_hrs"].iloc[-1]),
    ylim=(0.974 * 1e2, 1.004 * 1e2)
)

fig_spec.patch.set_facecolor('none')
fig_spec.savefig(f"transit_example_specLC_{binsize}.png", dpi=600)

