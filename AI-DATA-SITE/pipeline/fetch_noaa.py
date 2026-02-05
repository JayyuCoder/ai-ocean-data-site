import os
import xarray as xr
import pandas as pd
import requests
from datetime import date

def _download_if_needed(url, path):
    if not url or os.path.exists(path):
        return False
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        return True
    except Exception as e:
        print(f"WARNING: NOAA download failed for {path}: {type(e).__name__}")
        return False

def fetch_noaa_crw():
    sst_path = "NOAA_SST_FILE.nc"
    _download_if_needed(os.getenv("NOAA_SST_URL", ""), sst_path)
    if not os.path.exists(sst_path):
        # Fallback demo data if NOAA file is missing
        return pd.DataFrame(
            {
                "lat": [6.5, 6.6, 6.7],
                "lon": [92.5, 92.6, 92.7],
                "sst": [28.2, 28.4, 28.3],
                "dhw": [0.5, 0.6, 0.7],
                "date": [date.today()] * 3,
            }
        )

    ds = xr.open_dataset(sst_path)  # downloaded daily
    df = ds.to_dataframe().reset_index()

    # Prefer available DHW from dataset; fall back to 0.0 if missing
    cols = ["lat", "lon", "sst"]
    if "dhw" in df.columns:
        cols.append("dhw")
    df = df[cols]
    if "dhw" not in df.columns:
        df["dhw"] = 0.0
    df["date"] = date.today()
    return df

def fetch_noaa_ph():
    """
    Fetch pH data from NOAA Ocean Chemistry / Global Ocean Acidification Network (GOA-ON)
    """
    # Load pH NetCDF file (e.g., daily global pH product)
    ph_path = "NOAA_PH_FILE.nc"
    _download_if_needed(os.getenv("NOAA_PH_URL", ""), ph_path)
    if not os.path.exists(ph_path):
        # Fallback demo data if NOAA file is missing
        return pd.DataFrame(
            {
                "lat": [6.5, 6.6, 6.7],
                "lon": [92.5, 92.6, 92.7],
                "ph": [8.10, 8.11, 8.09],
                "date": [date.today()] * 3,
            }
        )

    ph_ds = xr.open_dataset(ph_path)
    ph_df = ph_ds.to_dataframe().reset_index()
    
    ph_df = ph_df[["lat", "lon", "ph"]]
    ph_df["date"] = date.today()
    return ph_df
