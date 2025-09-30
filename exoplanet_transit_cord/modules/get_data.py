import astropy.constants as c
from . import calculate_pars as pars
import numpy as np
import pyvo


def get_parameters(planet_name: str) -> dict:
    # Set the NASA Exoplanet Archive as the TAP ressource
    tap_resource = "https://exoplanetarchive.ipac.caltech.edu/TAP"
    tap_service = pyvo.dal.TAPService(tap_resource)

    # Generate the query string
    query_string = f"""
    SELECT pl_rade, pl_orbsmax, st_rad, st_teff,
    pl_orbincl, pl_orbeccen, pl_orblper, pl_projobliq, pl_imppar
    FROM ps WHERE default_flag = 1
    AND lower(pl_name) = '{planet_name.lower()}'
    """

    # Convert search result immediately to pandas DataFrame
    search_result = tap_service.search(query_string).to_table()

    # Very scuffed, but it works I guess
    result_dict = {
        key: search_result[key].value.data[0]
        for key in search_result.keys()
    }

    # Insert standardised argument of periapsis, projected obliquite, 
    # and orbital inclination if no value retrieved
    if np.isnan(result_dict["pl_orblper"]):
        result_dict["pl_orblper"] = 90.

    if np.isnan(result_dict["pl_projobliq"]):
        result_dict["pl_projobliq"] = 0.

    if np.isnan(result_dict["pl_orbincl"]):
        print("WAIT A MINUTE! I'll need to use retrieved b-value")

    # Calculate derivative parameters
    result_dict["ratio_ator"] = (
        result_dict["pl_orbsmax"] * c.au.value / (
            result_dict["st_rad"] * c.R_sun.value
        )
    )
    result_dict["ratio_rtor"] = (
        result_dict["pl_rade"] * c.R_earth.value / (
            result_dict["st_rad"] * c.R_sun.value
        )
    )

    # Calculate the impact parameter
    result_dict["impact_par"] = pars.calculate_impact_parameter(
        semimajor_axis=result_dict["ratio_ator"],
        orbit_inclination=result_dict["pl_orbincl"],
        eccentricity=result_dict["pl_orbeccen"],
        argument_periapsis=result_dict["pl_orblper"]
    )

    # Mark the file with current day for posterity
    # today = datetime.datetime.now().strftime("%Y-%m-%d")

    # Save search result as csv-file
    # search_result.to_csv(f"nasa_epa_fulldata_{today}.csv")
    return result_dict
