import h5py as h5
import numpy as np
# import matplotlib.pyplot as plt
import pandas as pd

# GLOBALS
PRESSURE_TARGET = 1e-3
TEMPERATURE_TARGET = 1000
BIN_TYPE = "resolution"
BIN_INFO = 100


def main():
    test = "1H2-16O__POKAZATEL__R15000_0.3-50mu.xsec.TauREx.h5"
    _ = prepare_xsec_data(f"/home/simon/Downloads/{test}")

    return


def prepare_xsec_data(filename: str):
    """Most importantly, bin down the xsec data."""
    xsec_data = h5.File(filename)
    reference = xsec_data["DOI"][()][0].decode("utf-8")
    mol_name = xsec_data["mol_name"][()][0].decode("utf-8")

    # Start the return dictionary
    xsec_dictionary = {
        "ref": reference,
        "name": mol_name,
        "latex_name": make_latex_string(mol_name),
    }

    # Find the appropriate xsec entry through pressure and temperature
    pressure = xsec_data["p"][()]
    p_idx = np.argmin(abs(np.log10(pressure) - np.log10(PRESSURE_TARGET)))

    temperature = xsec_data["t"][()]
    t_idx = np.argmin(abs(temperature - TEMPERATURE_TARGET))

    # Slice into xsec array
    xsec = xsec_data["xsecarr"][()]
    xsec_slice = xsec[p_idx][t_idx]

    # Document the chosen pressure and temperature
    xsec_dictionary["pt_doc_string"] = (
        f"Selected xsec at p = {pressure[p_idx]} bar "
        f"and T = {temperature[t_idx]} K"
    )

    # Wavelength from wavenumber array
    wavelength = 1 / (xsec_data["bin_edges"][()] * 1e2)

    # Bin down the data
    bin_info, wavel_bin, xsec_bin = wrap_bin_data(
        bin_type=BIN_TYPE, bin_info=BIN_INFO, wavel=wavelength, xsec=xsec_slice
    )

    # Turn around both arrays to have ascending wavelength
    xsec_dictionary["xsec"] = xsec_bin[::-1]
    xsec_dictionary["wavel"] = wavel_bin[::-1]
    xsec_dictionary["bin_information"] = bin_info

    # Saving binned xsec to a file
    saveframe = pd.DataFrame(
        data=np.array([xsec_dictionary["wavel"], xsec_dictionary["xsec"]]).T,
        columns=["wavel [m]", "x-sec"]
    )
    with open(f"binned_data/xsec_{xsec_dictionary['name']}.csv", "w") as f:
        f.write(
            f"# Name: {xsec_dictionary["name"]}\n"
            f"# Source: {xsec_dictionary["ref"]}\n"
            f"# From file: {filename}\n"
            f"# {xsec_dictionary["pt_doc_string"]}\n"
            f"# {xsec_dictionary["bin_information"]}\n"
        )
    saveframe.to_csv(
        f"binned_data/xsec_{xsec_dictionary['name']}.csv",
        mode="a", index=False
    )

    return xsec_dictionary


def wrap_bin_data(
        bin_type: str, bin_info: str,
        wavel: np.ndarray, xsec: np.ndarray
) -> tuple:
    """Wrap around different types of binning."""
    if bin_type.lower() == "resolution":
        info_str = f"Binned using R={bin_info}"
        idx_list = make_resolution_ids(wavel, bin_info)
        wavel_bin = index_list_average(wavel, idx_list)
        xsec_bin = index_list_average(xsec, idx_list)

    elif bin_type.lower() == "box":
        info_str = f"Binned box of size {bin_info}"
        wavel_bin = box_average(wavel, bin_info)
        xsec_bin = box_average(xsec, bin_info)

    return info_str, wavel_bin, xsec_bin


def index_list_average(data: np.ndarray, slices: np.ndarray) -> np.ndarray:
    """Custom average slices (e.g. for resolution-based binning)."""
    binned = np.array([
        np.average(data[slice_list]) for slice_list in slices
    ])

    return binned


def box_average(data: np.ndarray, window_size: int) -> np.ndarray:
    """Simple box average"""
    start = 0
    end = window_size
    box_averages = []

    # Loop through the array
    while end <= data.shape[0]:

        # Calculate the average of current window
        box_average = np.sum(data[start:end]) / window_size
        box_averages.append(box_average)

        # Shift window
        start = end
        end += window_size

    return box_averages


def make_resolution_ids(wavelength: np.ndarray, target_r: int) -> np.ndarray:
    """Create lists for slices correspinding to a certain resolution value."""
    # Some initial values
    start = 0
    end = 1
    r_tol = 1e-2
    result = []

    while end <= wavelength.shape[0]:
        current_r = 15000

        # Only using tolerance, break as soon as R is overshot
        while current_r - target_r > r_tol and current_r > target_r:

            # Slice into data and calculate resolution
            data_slice = wavelength[start:end + 1]
            lambda_central = np.average(data_slice)
            lambda_span = abs(data_slice[-1] - data_slice[0])
            current_r = lambda_central / lambda_span

            # Iterate into next slice size
            end += 1

            # Stop if max. array length is reached
            if end == wavelength.shape[0]:
                break

        # Add to list of slice indices
        slice_idxs = [idx for idx in range(start, end)]
        result.append(slice_idxs)

        # Start next iteration
        start = end
        end += 1

    return result


def make_latex_string(string: str) -> str:
    """Make e.g. H2O into H$_2$O"""
    new_string = ""

    for element in string:
        try:
            new_string += f"$_{int(element)}$"
        except ValueError:
            new_string += element

    return new_string


if __name__ == "__main__":
    main()
