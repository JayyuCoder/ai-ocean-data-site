import xarray as xr
import pandas as pd
from datetime import date

def fetch_noaa_crw():
    ds = xr.open_dataset("NOAA_SST_FILE.nc")  # downloaded daily
    df = ds.to_dataframe().reset_index()

    df = df[["lat", "lon", "sst"]]
    df["date"] = date.today()
    return df

def fetch_noaa_ph():
    """
    Fetch pH data from NOAA Ocean Chemistry / Global Ocean Acidification Network (GOA-ON)
    """
    # Load pH NetCDF file (e.g., daily global pH product)
    ph_ds = xr.open_dataset("NOAA_PH_FILE.nc")
    ph_df = ph_ds.to_dataframe().reset_index()
    
    ph_df = ph_df[["lat", "lon", "ph"]]
    ph_df["date"] = date.today()
    return ph_df
