from prometheus_client import Counter, Gauge, Summary
import os

# Metrics
pipeline_runs = Counter('ai_pipeline_runs_total', 'Total number of pipeline runs')
pipeline_duration = Summary('ai_pipeline_duration_seconds', 'Time spent running pipeline')
scheduler_runs = Counter('ai_scheduler_runs_total', 'Total number of scheduler job triggers')
last_pipeline_success = Gauge('ai_pipeline_last_success_timestamp', 'Last successful pipeline run (unix timestamp)')

def configure_from_env():
    # placeholder for future config
    return {
        'metrics_port': int(os.getenv('METRICS_PORT', '8002'))
    }
