import time
import os
import sys
from prometheus_client import start_http_server, Gauge
import sqlite3
from datetime import datetime

# ensure project root is on path for imports
if __name__ == '__main__' and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from monitoring.metrics import configure_from_env

# Ocean data metrics
avg_sst_gauge = Gauge('ocean_avg_sst_celsius', 'Average Sea Surface Temperature')
avg_ph_gauge = Gauge('ocean_avg_ph', 'Average pH')
avg_health_gauge = Gauge('ocean_avg_health_score', 'Average Coral Health Score')
record_count_gauge = Gauge('ocean_records_total', 'Total ocean metric records')

def update_ocean_metrics():
    """Query DB and update Prometheus gauges with latest ocean data"""
    try:
        db_path = 'ocean_demo.db'
        if not os.path.exists(db_path):
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get latest averages
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
