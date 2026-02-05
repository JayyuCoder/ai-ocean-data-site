import geopandas as gpd
from sqlalchemy import create_engine
import os

DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ocean_db")
engine = create_engine(DB_URL)

def spatial_merge(noaa_df, allen_gdf=None):
    """
    Spatial join: NOAA points with coral reef polygons.
    Prefer Allen WFS GeoDataFrame if provided; fallback to PostGIS.
    """
    # Use Allen WFS data if available
    if allen_gdf is not None and not allen_gdf.empty:
        noaa_gdf = gpd.GeoDataFrame(
            noaa_df,
            geometry=gpd.points_from_xy(noaa_df.lon, noaa_df.lat),
            crs="EPSG:4326"
        )
        try:
            merged = gpd.sjoin(noaa_gdf, allen_gdf, how="left")
            return merged
        except Exception as e:
            print(f"WARNING: Spatial join with Allen data failed ({type(e).__name__})")

    # Fallback to PostGIS
    try:
        reefs = gpd.read_postgis("SELECT * FROM coral_reefs", engine, geom_col="geom")
    except Exception as e:
        print(f"WARNING: PostGIS unavailable ({type(e).__name__}); skipping spatial merge")
        return noaa_df

    noaa_gdf = gpd.GeoDataFrame(
        noaa_df,
        geometry=gpd.points_from_xy(noaa_df.lon, noaa_df.lat),
        crs="EPSG:4326"
    )
    merged = gpd.sjoin(noaa_gdf, reefs, how="inner")
    return merged

def integrate_ph(noaa_df, ph_df):
    """
    Merge pH data with NOAA data by location and date
    """
    return noaa_df.merge(
        ph_df,
        on=["lat", "lon", "date"],
        how="left"
    )
