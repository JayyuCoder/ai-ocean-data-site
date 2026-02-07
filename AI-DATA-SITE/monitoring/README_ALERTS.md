Prometheus Alerting Notes

1. Alert Rules
   - File: monitoring/alert_rules.yml
   - Rules added:
     - HighSST: triggers when `ocean_avg_sst_celsius > 29` for 10m
     - ManyAnomalies: triggers when >100 new records in 1h

2. Alertmanager
   - Config: monitoring/alertmanager.yml
   - Currently configured with a trivial webhook receiver (127.0.0.1:5001). Update to your actual notification endpoint (Slack, email gateway, PagerDuty) before enabling real alerts.

3. Docker Compose
   - `deploy/docker-compose-grafana.yml` now includes `alertmanager` service and mounts rule files for Prometheus.

4. To enable alerts locally
   - Start monitoring stack:
     ```bash
     cd AI-DATA-SITE/deploy
     docker-compose -f docker-compose-grafana.yml up -d
     ```
   - Check Prometheus targets: http://localhost:9090/targets
   - Check Alertmanager UI: http://localhost:9093

5. Production
   - Replace webhook receiver in `monitoring/alertmanager.yml` with your notification integration.
   - Consider using secure credentials and secrets for SMTP/Slack.
