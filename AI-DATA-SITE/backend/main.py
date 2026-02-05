from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.database import SessionLocal, init_db, get_db
from backend.models import OceanMetrics
from datetime import datetime, timedelta

app = FastAPI(
    title="AI Ocean Data API",
    description="Real-time coral reef health monitoring",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    """Initialize database on startup (skip if no PostgreSQL)"""
    try:
        init_db()
    except Exception as e:
        print(f"WARNING: Database initialization skipped: {type(e).__name__}")
        print("Running in demo mode without persistent storage")
        print("To enable full features, ensure PostgreSQL is running on localhost:5432")

@app.get("/")
async def root():
    return {
        "status": "running",
        "version": "1.0.0",
        "service": "AI Ocean Data API"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/data/latest")
async def get_latest_data(db: Session = Depends(get_db)):
    """Get latest ocean metrics"""
    latest = db.query(OceanMetrics).order_by(OceanMetrics.date.desc()).first()
    if latest:
        return {
            "date": latest.date,
            "latitude": latest.latitude,
            "longitude": latest.longitude,
            "sst": latest.sst,
            "dhw": latest.dhw,
            "ph": latest.ph,
            "health_score": latest.health_score,
            "anomaly": latest.anomaly,
            "forecast_ph": latest.forecast_ph
        }
    return {"error": "No data available"}

@app.get("/data/timeseries")
async def get_timeseries(days: int = 30, db: Session = Depends(get_db)):
    """Get time-series data for the last N days"""
    cutoff_date = datetime.now() - timedelta(days=days)
    records = db.query(OceanMetrics).filter(
        OceanMetrics.date >= cutoff_date
    ).order_by(OceanMetrics.date).all()

    return [
        {
            "date": r.date.isoformat(),
            "latitude": r.latitude,
            "longitude": r.longitude,
            "sst": r.sst,
            "ph": r.ph,
            "health_score": r.health_score,
            "anomaly": r.anomaly
        }
        for r in records
    ]

@app.get("/data/anomalies")
async def get_anomalies(db: Session = Depends(get_db)):
    """Get recent anomalies detected"""
    anomalies = db.query(OceanMetrics).filter(
        OceanMetrics.anomaly == True
    ).order_by(OceanMetrics.date.desc()).limit(50).all()

    return [
        {
            "date": a.date.isoformat(),
            "latitude": a.latitude,
            "longitude": a.longitude,
            "sst": a.sst,
            "health_score": a.health_score
        }
        for a in anomalies
    ]

@app.get("/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """Get aggregate statistics"""
    from sqlalchemy import func, case

    stats = db.query(
        func.avg(OceanMetrics.sst).label("avg_sst"),
        func.avg(OceanMetrics.ph).label("avg_ph"),
        func.avg(OceanMetrics.health_score).label("avg_health"),
        func.sum(case((OceanMetrics.anomaly == True, 1), else_=0)).label("anomaly_count")
    ).first()

    return {
        "avg_sst": float(stats.avg_sst or 0),
        "avg_ph": float(stats.avg_ph or 0),
        "avg_health_score": float(stats.avg_health or 0),
        "anomalies_detected": stats.anomaly_count or 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
