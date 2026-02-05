import geopandas as gpd
from sqlalchemy import create_engine
import os

DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ocean_db")
engine = create_engine(DB_URL)

def spatial_merge(noaa_df):
    """
    Spatial join: NOAA points with Coral Reef polygons from PostGIS
    """
    # Load reef polygons from PostGIS
    reefs = gpd.read_postgis("SELECT * FROM coral_reefs", engine, geom_col="geom")
    
    # Convert NOAA dataframe to GeoDataFrame with point geometry
    noaa_gdf = gpd.GeoDataFrame(
        noaa_df,
        geometry=gpd.points_from_xy(noaa_df.lon, noaa_df.lat),
        crs="EPSG:4326"
    )
    
    # Spatial join: points within reef polygons
    merged = gpd.sjoin(noaa_gdf, reefs, how="inner")
    return merged

def integrate_ph(noaa_df, ph_df):
    """
    Merge pH data with NOAA data by location and date
    """
    return noaa_df.merge(
        ph_df,
        on=["latitude", "longitude", "date"],
        how="left"
    )
