import os
import requests
import pandas as pd
import geopandas as gpd
import shapely.geometry as geom
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

def _parse_bbox(bbox_str):
    try:
        parts = [float(x) for x in bbox_str.split(",")]
        if len(parts) == 4:
            return parts
    except Exception:
        pass
    return None

def _compute_bbox_from_noaa(noaa_df, pad=0.1):
    if noaa_df is None or noaa_df.empty:
        return None
    minx = float(noaa_df["lon"].min()) - pad
    maxx = float(noaa_df["lon"].max()) + pad
    miny = float(noaa_df["lat"].min()) - pad
    maxy = float(noaa_df["lat"].max()) + pad
    return [minx, miny, maxx, maxy]

def _fallback_gdf():
    return gpd.GeoDataFrame(
        pd.DataFrame({
            "reef_type": ["Fringing Reef"],
            "reef_health_baseline": [85]
        }),
        geometry=[geom.Point(80.0, 15.0)],
        crs="EPSG:4326"
    )

def fetch_allen_coral_atlas(noaa_df=None):
    """
    Fetch Allen Coral Atlas reef polygons via WFS (GeoJSON).
    Returns a GeoDataFrame with reef polygons and attributes.
    """
    wfs_url = os.getenv("ALLEN_WFS_URL", "").strip()
    layer = os.getenv("ALLEN_WFS_LAYER", "").strip()
    bbox_env = os.getenv("ALLEN_WFS_BBOX", "").strip()

    if not wfs_url or not layer:
        return _fallback_gdf()

    bbox = _parse_bbox(bbox_env) or _compute_bbox_from_noaa(noaa_df)
    params = {
        "service": "WFS",
        "version": "1.0.0",
        "request": "GetFeature",
        "typename": layer,
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
    }
    if bbox:
        params["bbox"] = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"

    try:
        r = requests.get(
            wfs_url,
            params=params,
            headers={"User-Agent": "AI-Ocean-Data-Site/1.0"},
            timeout=60
        )
        if r.status_code != 200:
            print("Allen WFS status:", r.status_code)
            print("Allen WFS response:", r.text[:300])
            return _fallback_gdf()

        data = r.json()
        gdf = gpd.GeoDataFrame.from_features(data["features"], crs="EPSG:4326")
        return gdf
    except Exception as e:
        print(f"WARNING: Allen Coral Atlas WFS failed: {type(e).__name__}")
        return _fallback_gdf()
