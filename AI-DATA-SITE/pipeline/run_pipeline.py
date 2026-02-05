import os
import sys

# Allow running as a script: python pipeline/run_pipeline.py
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pipeline.fetch_noaa import fetch_noaa_crw, fetch_noaa_ph
from pipeline.fetch_allen import fetch_allen_coral_atlas
from pipeline.clean_transform import clean_noaa, clean_allen
from pipeline.merge_data import spatial_merge, integrate_ph
from ml.model import health_score, detect_anomaly, train_lstm, forecast_lstm
import backend.database as db
from backend.models import OceanMetrics
import pandas as pd

def run_daily_pipeline():
    """
    6:00 AM Master Pipeline
    1. Fetch NOAA CRW (SST, DHW) + pH
    2. Fetch Allen Coral Atlas
    3. Clean & Transform
    4. Spatial Merge (PostGIS)
    5. LSTM Forecasting
    6. Anomaly Detection
    7. Store to PostgreSQL
    """

    # Step 1: Fetch data
    print("Step 1: Fetching NOAA CRW data...")
    noaa = fetch_noaa_crw()
    ph = fetch_noaa_ph()

    print("Step 2: Fetching Allen Coral Atlas...")
    allen = fetch_allen_coral_atlas()

    # Step 2: Clean
    print("Step 3: Cleaning data...")
    noaa = clean_noaa(noaa)
    allen = clean_allen(allen)

    # Step 3: Integrate pH data
    print("Step 4: Integrating pH data...")
    merged = integrate_ph(noaa, ph)

    # Step 4: Spatial merge with PostGIS
    print("Step 5: Spatial merge with coral reefs...")
    merged = spatial_merge(merged)

    # Step 5: ML Predictions
    print("Step 6: Running ML predictions...")

    # Health score
    merged["health_score"] = merged.apply(health_score, axis=1)

    # LSTM forecasting for pH (next 7 days)
    merged["forecast_ph"] = None
    if len(merged) >= 30 and merged["ph"].notna().sum() >= 30:
        try:
            lstm_model = train_lstm(merged["ph"].values)
            forecast = forecast_lstm(lstm_model, merged["ph"].values, steps_ahead=7)
            # Store the next-step forecast on the latest row
            merged.loc[merged.index[-1], "forecast_ph"] = float(forecast[0])
        except Exception as e:
            print(f"LSTM forecast error: {e}")

    # Anomaly detection
    merged["anomaly"] = detect_anomaly(merged["sst"])

    # Step 6: Store to PostgreSQL
    print("Step 7: Storing to PostgreSQL...")
    db.init_db()
    if db.SessionLocal is None:
        raise RuntimeError("Database session not initialized")
    db_session = db.SessionLocal()
    for _, row in merged.iterrows():
        record = OceanMetrics(
            date=row["date"],
            latitude=row["lat"],
            longitude=row["lon"],
            sst=row["sst"],
            dhw=row.get("dhw", None),
            ph=row.get("ph", None),
            health_score=row["health_score"],
            anomaly=row["anomaly"],
            forecast_ph=row.get("forecast_ph", None),
        )
        db_session.add(record)

    db_session.commit()
    db_session.close()
    print("Pipeline completed successfully!")

if __name__ == "__main__":
    run_daily_pipeline()
