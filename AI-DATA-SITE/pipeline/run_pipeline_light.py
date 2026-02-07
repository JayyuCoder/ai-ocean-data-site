import os
import sys
from datetime import date

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pipeline.fetch_noaa import fetch_noaa_crw, fetch_noaa_ph
from pipeline.fetch_allen import fetch_allen_coral_atlas
from pipeline.clean_transform import clean_noaa, clean_allen
import geopandas as gpd
import pandas as pd

import backend.database as db
from backend.models import OceanMetrics
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import insert as pg_insert

# instrumentation
try:
    from monitoring.metrics import pipeline_runs, last_pipeline_success, pipeline_duration
except Exception:
    pipeline_runs = None
    last_pipeline_success = None
    pipeline_duration = None


def health_score_row(row):
    baseline = row.get("reef_health_baseline", 80)
    dhw = row.get("dhw", 0)
    score = baseline - (row.get("sst", 0) * 1.5 + dhw * 5)
    return max(score, 0)


def run_light_pipeline():
    print("[light pipeline] Fetching NOAA CRW data...")
    if pipeline_runs:
        pipeline_runs.inc()
    timer = pipeline_duration.time() if pipeline_duration else None
    noaa = fetch_noaa_crw()
    print("[light pipeline] Fetching pH data (if available)...")
    ph = fetch_noaa_ph()

    print("[light pipeline] Fetching Allen Coral Atlas data (geo)...")
    allen = fetch_allen_coral_atlas(noaa_df=noaa)

    print("[light pipeline] Cleaning data...")
    noaa = clean_noaa(noaa)
    if isinstance(allen, gpd.GeoDataFrame):
        allen = clean_allen(allen)

    print("[light pipeline] Integrating pH data...")
    merged = noaa.merge(ph, on=["lat", "lon", "date"], how="left")

    # Spatial join with Allen if available
    try:
        if isinstance(allen, gpd.GeoDataFrame) and not allen.empty:
            noaa_gdf = gpd.GeoDataFrame(
                merged,
                geometry=gpd.points_from_xy(merged.lon, merged.lat),
                crs="EPSG:4326"
            )
            merged = gpd.sjoin(noaa_gdf, allen, how="left")
            # convert back to DataFrame
            merged = pd.DataFrame(merged.drop(columns=["geometry"]))
    except Exception as e:
        print(f"[light pipeline] Spatial join skipped: {e}")

    # Compute health score and simple anomaly flag
    print("[light pipeline] Computing health score and anomalies...")
    merged["health_score"] = merged.apply(health_score_row, axis=1)
    merged["anomaly"] = False
    merged["forecast_ph"] = None

    # Prepare records for DB insert
    records = merged.rename(columns={"lat": "latitude", "lon": "longitude"})
    records = records[["date", "latitude", "longitude", "sst", "dhw", "ph", "health_score", "anomaly", "forecast_ph"]]
    records = records.to_dict(orient="records")

    print(f"[light pipeline] Inserting {len(records)} rows into SQLite DB...")
    db.init_db()
    session = db.SessionLocal()
    # detect if backing engine is Postgres to use upsert
    dialect_name = None
    try:
        dialect_name = db.engine.dialect.name
    except Exception:
        pass
    for rec in records:
        # ensure date is date object
        if isinstance(rec.get("date"), str):
            try:
                rec["date"] = pd.to_datetime(rec["date"]).date()
            except Exception:
                rec["date"] = date.today()

        payload = {
            "date": rec.get("date"),
            "latitude": float(rec.get("latitude", 0)),
            "longitude": float(rec.get("longitude", 0)),
            "sst": float(rec.get("sst", 0)),
            "dhw": float(rec.get("dhw", 0)),
            "ph": rec.get("ph"),
            "health_score": float(rec.get("health_score", 0)),
            "anomaly": bool(rec.get("anomaly", False)),
            "forecast_ph": rec.get("forecast_ph", None),
        }
        if dialect_name == "postgresql":
            # perform upsert using ON CONFLICT on (date, latitude, longitude)
            table = OceanMetrics.__table__
            stmt = pg_insert(table).values(**payload)
            update_cols = {c.name: stmt.excluded[c.name] for c in table.c if c.name not in ("id",)}
            stmt = stmt.on_conflict_do_update(index_elements=["date", "latitude", "longitude"],
                                              set_=update_cols)
            session.execute(stmt)
        else:
            om = OceanMetrics(**payload)
            session.add(om)
    try:
        session.commit()
        print(f"[light pipeline] Inserted/updated {len(records)} rows")
    except Exception as e:
        session.rollback()
        print(f"[light pipeline] Error committing rows: {e}")
    finally:
        session.close()

    print("[light pipeline] Completed successfully.")
    if timer:
        timer.observe_duration()
    if last_pipeline_success:
        import time as _t
        last_pipeline_success.set(int(_t.time()))


if __name__ == "__main__":
    run_light_pipeline()
