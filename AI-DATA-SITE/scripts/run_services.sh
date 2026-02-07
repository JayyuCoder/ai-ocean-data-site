#!/usr/bin/env bash
# Simple helper to start backend, frontend, and scheduler in separate terminals
# Usage: ./scripts/run_services.sh

echo "Starting backend (uvicorn) in background..."
nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
echo "Backend started (logs -> backend.log)"

echo "Starting streamlit frontend in background..."
nohup streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0 > frontend.log 2>&1 &
echo "Frontend started (logs -> frontend.log)"

echo "Starting scheduler (runs pipeline daily) in background..."
nohup python scheduler/scheduler.py > scheduler.log 2>&1 &
echo "Scheduler started (logs -> scheduler.log)"

echo "Starting metrics server in background..."
nohup python monitoring/metrics_server.py > metrics.log 2>&1 &
echo "Metrics server started (logs -> metrics.log)"
