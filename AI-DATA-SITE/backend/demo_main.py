#!/usr/bin/env python
"""
Minimal FastAPI demo without database dependencies.
Demonstrates the API structure and can be extended.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Dict

app = FastAPI(
    title="AI Ocean Data API (Demo)",
    description="Real-time coral reef health monitoring - Demo Mode",
    version="1.0.0-demo"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Demo data
DEMO_METRICS = {
    "latest": {
        "timestamp": datetime.now().isoformat(),
        "latitude": 6.5,
        "longitude": 92.5,
        "sst": 28.5,
        "dhw": 0.8,
        "ph": 8.1,
        "health_score": 78.5,
        "anomaly": False
    },
    "timeseries": [
        {"date": "2026-01-31", "sst": 28.2, "ph": 8.12, "dhw": 0.5, "health_score": 80.0},
        {"date": "2026-02-01", "sst": 28.3, "ph": 8.11, "dhw": 0.6, "health_score": 79.5},
        {"date": "2026-02-02", "sst": 28.4, "ph": 8.10, "dhw": 0.7, "health_score": 78.5},
        {"date": "2026-02-03", "sst": 28.5, "ph": 8.09, "dhw": 0.8, "health_score": 77.0},
        {"date": "2026-02-04", "sst": 28.5, "ph": 8.10, "dhw": 0.8, "health_score": 78.5},
    ],
    "anomalies": [
        {"date": "2026-02-03", "type": "high_sst", "severity": "medium", "description": "SST elevated by 1.2°C"}
    ],
    "stats": {
        "sst_min": 27.8,
        "sst_max": 29.2,
        "sst_mean": 28.3,
        "sst_std": 0.4,
        "ph_min": 8.08,
        "ph_max": 8.14,
        "ph_mean": 8.10,
        "ph_std": 0.02,
        "health_score_min": 65.0,
        "health_score_max": 85.0,
        "health_score_mean": 76.7,
    },
    "forecast": {
        "forecast_date": (datetime.now()).isoformat(),
        "days_ahead": 7,
        "sst_forecast": [28.5, 28.6, 28.7, 28.6, 28.5, 28.4, 28.3],
        "ph_forecast": [8.10, 8.09, 8.09, 8.10, 8.11, 8.12, 8.12],
        "confidence": 0.92,
        "model": "LSTM (7-layer)"
    }
}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to AI Ocean Data API (Demo Mode)",
        "mode": "demo",
        "version": "1.0.0",
        "note": "Running without database (PostgreSQL not connected)",
        "endpoints": {
            "/": "This message",
            "/health": "System health check",
            "/latest": "Get latest ocean metrics",
            "/timeseries": "Get historical timeseries data",
            "/stats": "Get aggregate statistics",
            "/anomalies": "Get detected anomalies",
            "/forecast": "Get 7-day forecast",
            "/docs": "Interactive API documentation (Swagger UI)"
        },
        "data_sources": [
            "NOAA Coral Reef Watch (simulated)",
            "Allen Coral Atlas (simulated)",
            "Global Ocean Acidification Network (simulated)"
        ]
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "demo",
        "database": "disconnected (PostgreSQL not available)",
        "api_version": "1.0.0"
    }

@app.get("/latest")
async def get_latest():
    """Get latest ocean metrics for a reef"""
    return {
        "success": True,
        "data": DEMO_METRICS["latest"],
        "source": "demo (no database)"
    }

@app.get("/timeseries")
async def get_timeseries(days: int = 7):
    """Get historical timeseries data"""
    return {
        "success": True,
        "days_requested": days,
        "data": DEMO_METRICS["timeseries"][:days],
        "count": min(days, len(DEMO_METRICS["timeseries"])),
        "source": "demo (no database)"
    }

@app.get("/stats")
async def get_stats():
    """Get aggregate statistics"""
    return {
        "success": True,
        "data": DEMO_METRICS["stats"],
        "period_days": 30,
        "source": "demo (no database)"
    }

@app.get("/anomalies")
async def get_anomalies():
    """Get detected anomalies"""
    return {
        "success": True,
        "count": len(DEMO_METRICS["anomalies"]),
        "data": DEMO_METRICS["anomalies"],
        "detection_method": "Isolation Forest (simulated)",
        "source": "demo (no database)"
    }

@app.post("/forecast")
async def forecast(days: int = 7):
    """Get 7-day ahead forecast"""
    forecast_data = DEMO_METRICS["forecast"].copy()
    forecast_data["days_ahead"] = days
    return {
        "success": True,
        "data": forecast_data,
        "source": "demo (LSTM simulation)"
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting AI Ocean Data API (Demo Mode)...")
    print("Dashboard: http://localhost:8501")
    print("API Docs:  http://localhost:8000/docs")
    print("API Root:  http://localhost:8000")
    print()
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
