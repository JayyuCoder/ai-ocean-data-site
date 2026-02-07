import time
import os
import sys
from prometheus_client import start_http_server, Gauge, Info
import sqlite3
from datetime import datetime, timedelta

# ensure project root is on path for imports
if __name__ == '__main__' and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from monitoring.metrics import configure_from_env

# Ocean data metrics - global averages
avg_sst_gauge = Gauge('ocean_avg_sst_celsius', 'Average Sea Surface Temperature')
avg_ph_gauge = Gauge('ocean_avg_ph', 'Average pH')
avg_health_gauge = Gauge('ocean_avg_health_score', 'Average Coral Health Score')
record_count_gauge = Gauge('ocean_records_total', 'Total ocean metric records')

# Per-day metrics (last 3 days)
sst_last_day = Gauge('ocean_sst_last_day_celsius', 'SST last day', ['day'])
ph_last_day = Gauge('ocean_ph_last_day', 'pH last day', ['day'])
health_last_day = Gauge('ocean_health_last_day', 'Health score last day', ['day'])

def update_ocean_metrics():
    """Query DB and update Prometheus gauges with ocean data and trends"""
    try:
        db_path = 'ocean_demo.db'
        if not os.path.exists(db_path):
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get latest averages (global)
        cursor.execute('''
            SELECT 
                AVG(sst) as avg_sst,
                AVG(ph) as avg_ph,
                AVG(health_score) as avg_health,
                COUNT(*) as total_records
            FROM ocean_metrics
        ''')
        
        row = cursor.fetchone()
        if row:
            avg_sst, avg_ph, avg_health, total = row
            avg_sst_gauge.set(avg_sst if avg_sst else 0)
            avg_ph_gauge.set(avg_ph if avg_ph else 0)
            avg_health_gauge.set(avg_health if avg_health else 0)
            record_count_gauge.set(total if total else 0)
        
        # Get last 3 days of data (daily averages)
        cursor.execute('''
            SELECT 
                date,
                AVG(sst) as daily_sst,
                AVG(ph) as daily_ph,
                AVG(health_score) as daily_health
            FROM ocean_metrics
            GROUP BY date
            ORDER BY date DESC
            LIMIT 3
        ''')
        
        days_data = cursor.fetchall()
        for row in days_data:
            date_str, daily_sst, daily_ph, daily_health = row
            sst_last_day.labels(day=date_str).set(daily_sst if daily_sst else 0)
            ph_last_day.labels(day=date_str).set(daily_ph if daily_ph else 0)
            health_last_day.labels(day=date_str).set(daily_health if daily_health else 0)
        
        conn.close()
    except Exception as e:
        print(f"Error updating metrics: {e}")

def main():
    cfg = configure_from_env()
    port = cfg.get('metrics_port', 8002)
    start_http_server(port)
    print(f"Prometheus metrics server started on :{port}")
    
    # Update metrics immediately and every 30 seconds
    update_ocean_metrics()
    
    try:
        while True:
            time.sleep(30)
            update_ocean_metrics()
    except KeyboardInterrupt:
        print("Metrics server stopping")

if __name__ == '__main__':
    main()
