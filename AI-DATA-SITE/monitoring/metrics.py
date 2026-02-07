from prometheus_client import Counter, Gauge, Summary
import os

# Metrics
pipeline_runs = Counter('ai_pipeline_runs_total', 'Total number of pipeline runs')
pipeline_duration = Summary('ai_pipeline_duration_seconds', 'Time spent running pipeline')
scheduler_runs = Counter('ai_scheduler_runs_total', 'Total number of scheduler job triggers')
last_pipeline_success = Gauge('ai_pipeline_last_success_timestamp', 'Last successful pipeline run (unix timestamp)')

# Retry metrics
pipeline_fetches_total = Counter('ai_pipeline_fetches_total', 'Total fetch attempts', ['source'])
pipeline_fetch_retries = Counter('ai_pipeline_fetch_retries_total', 'Total retries across all fetches', ['source', 'reason'])
pipeline_fetch_failures = Counter('ai_pipeline_fetch_failures_total', 'Total fetch failures (all retries exhausted)', ['source'])
pipeline_fetch_success_rate = Gauge('ai_pipeline_fetch_success_rate', 'Success rate of fetches (0-100)', ['source'])

def configure_from_env():
    # placeholder for future config
    return {
        'metrics_port': int(os.getenv('METRICS_PORT', '8002'))
    }
