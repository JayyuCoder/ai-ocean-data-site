# Deployment & Operations Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Local Development](#local-development)
3. [Database Configuration](#database-configuration)
4. [Monitoring & Alerts](#monitoring--alerts)
5. [Pipeline Management](#pipeline-management)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- PostgreSQL (optional; SQLite fallback available)
- 2GB RAM, 5GB disk space recommended

### Local Setup (Development)

```bash
# 1. Clone and navigate
git clone https://github.com/JayyuCoder/ai-ocean-data-site.git
cd ai-ocean-data-site

# 2. Create Python environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r AI-DATA-SITE/requirements.txt

# 4. Start services (SQLite + local backend)
cd AI-DATA-SITE
python3 backend/main.py           # Terminal 1: Backend on :8000
python3 frontend/app.py           # Terminal 2: Frontend on :8501
python3 monitoring/metrics_server.py  # Terminal 3: Metrics on :8002
python3 scheduler/scheduler.py    # Terminal 4: Scheduler (hourly updates)
```

### Local Setup (with Monitoring Stack)

```bash
# Start Postgres, Prometheus, Grafana (docker-compose)
cd AI-DATA-SITE
docker-compose up -d db prometheus grafana

# Backend + services use Postgres (recommended for testing)
export DATABASE_URL=postgresql://ocean_user:ocean_secure_password@localhost:5432/ocean_db
python3 backend/main.py
python3 frontend/app.py
python3 monitoring/metrics_server.py
python3 scheduler/scheduler.py

# Access services:
# - Frontend: http://localhost:8501
# - Backend API: http://localhost:8000
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)
```

---

## Local Development

### Running the Light Pipeline

```bash
# Fetch NOAA SST + DHW, Allen Coral Atlas, and insert into DB
cd AI-DATA-SITE
DATABASE_URL=postgresql://... python3 pipeline/run_pipeline_light.py
```

**Features:**
- Exponential backoff retry on network timeouts (up to 3 attempts)
- Automatic fallback to demo data if API unavailable
- SQLite or Postgres support via `DATABASE_URL` env var
- UPSERT logic prevents duplicate rows on Postgres
- Logs detailed progress

### Reviewing Data

```bash
# Via Backend API
curl http://localhost:8000/data/latest | jq
curl http://localhost:8000/stats | jq
curl http://localhost:8000/data/timeseries?days=7 | jq

# Via Frontend
# Open http://localhost:8501 in browser
```

---

## Database Configuration

### SQLite (Default, Local Development)

- **File**: `AI-DATA-SITE/ocean_demo.db`
- **Setup**: Automatic (creates on first run)
- **Pros**: No external dependencies, quick start
- **Cons**: No spatial queries, single-threaded

### PostgreSQL (Recommended for Production)

#### Setup Postgres Locally

```bash
# Using Docker
docker-compose up -d db

# Or install PostgreSQL and create database
createdb -U postgres ocean_db
psql -U postgres ocean_db -c "CREATE EXTENSION postgis;"
```

#### Migration from SQLite → Postgres

```bash
# Install Postgres driver
pip install psycopg2-binary

# Run migration script
DATABASE_URL=postgresql://ocean_user:ocean_secure_password@localhost:5432/ocean_db \
  python3 scripts/migrate_sqlite_to_postgres.py
```

#### Connection String

```bash
# Local development
export DATABASE_URL=postgresql://ocean_user:ocean_secure_password@localhost:5432/ocean_db

# Production (example)
export DATABASE_URL=postgresql://user:password@prod-db.example.com:5432/ocean_prod
```

#### PostGIS Functions

Enable spatial queries:

```sql
CREATE EXTENSION postgis;

-- Find reefs within 50km of a point
SELECT * FROM ocean_metrics 
WHERE ST_DWithin(
  ST_Point(longitude, latitude)::geography,
  ST_Point(92.5, 6.5)::geography,
  50000  -- meters
);
```

---

## Monitoring & Alerts

### Prometheus

**Configuration**: `AI-DATA-SITE/monitoring/prometheus.yml`

```yaml
scrape_configs:
  - job_name: 'ai_ocean_metrics'
    static_configs:
      - targets: ['localhost:8002']
```

**Access**: http://localhost:9090

**Key Metrics Exposed**:
- `ocean_avg_sst_celsius` — Average sea surface temperature
- `ocean_avg_ph` — Average water pH
- `ocean_avg_health_score` — Reef health baseline
- `ocean_records_total` — Total measurements in DB
- `ocean_sst_last_day_celsius{day="..."}` — Per-day SST

### Alert Rules

**File**: `AI-DATA-SITE/monitoring/alert_rules.yml`

**Configured Alerts**:
1. **HighSST**: Fires when avg SST > 29°C for 10+ minutes
2. **ManyAnomalies**: Fires when anomalies > 100 in 1 hour

**View Rules**:
```bash
curl http://localhost:9090/api/v1/alerts
```

### Alertmanager Configuration

**File**: `AI-DATA-SITE/monitoring/alertmanager.yml`

#### Enable Slack Notifications

```yaml
receivers:
  - name: 'critical'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#ocean-alerts'
        title: '🚨 {{ .GroupLabels.alertname }}'
        text: '{{ .CommonAnnotations.summary }}'
        send_resolved: true
```

1. Create Slack app: https://api.slack.com/apps
2. Enable Incoming Webhooks
3. Create new webhook for your channel
4. Update `alertmanager.yml` with webhook URL
5. Restart Alertmanager: `docker-compose restart alertmanager`

#### Enable Email Notifications

```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'  # Use app-specific password
  smtp_from: 'alerts@example.com'

receivers:
  - name: 'warning'
    email_configs:
      - to: 'team@example.com'
        headers:
          Subject: '⚠️ Ocean Alert: {{ .GroupLabels.alertname }}'
```

### Grafana Dashboards

**Access**: http://localhost:3000 (default: admin/admin)

**Pre-provisioned Dashboards**:
- **Ocean Overview** — Live SST, pH, health score, anomaly count
- **Ocean Trends** — 3-day rolling metrics
- **Ocean Live** — Real-time per-day metrics with time picker

**Custom Dashboard Setup**:
1. Create new dashboard
2. Add Prometheus data source: http://prometheus:9090
3. Query ocean_* metrics
4. Save and share

---

## Pipeline Management

### Scheduler Modes

**Hourly Live Mode** (default):
```bash
# Fetches and updates data every hour
python3 scheduler/scheduler.py
```

**Daily Mode**:
```bash
# Edit scheduler/scheduler.py and change:
# SCHED_MODE = "daily"  # Instead of "hourly"
python3 scheduler/scheduler.py
```

**Manual One-Shot**:
```bash
python3 pipeline/run_pipeline_light.py
```

### Retry Logic

The pipeline now includes exponential backoff:
- **Max retries**: 3 attempts per URL
- **Backoff factor**: 2x (1s → 2s → 4s)
- **Timeout**: 60s per request
- **Fallback**: Demo data if all retries fail

Example output:
```
[light pipeline] Fetching NOAA CRW data...
[fetch] Timeout, retrying in 1s...
[fetch] Timeout, retrying in 2s...
[light pipeline] Fetched 150 rows
```

### Logs

- **Pipeline**: Stdout + `logs/pipeline.log`
- **Scheduler**: `logs/scheduler.log`
- **Backend**: Stdout/uvicorn logs
- **Prometheus**: Docker logs: `docker logs prometheus`

```bash
# Tail scheduler log
tail -f AI-DATA-SITE/logs/scheduler.log

# Tail pipeline logs
tail -f AI-DATA-SITE/logs/pipeline.log
```

---

## Production Deployment

### Pre-Production Checklist

- [ ] PostgreSQL running with daily backups
- [ ] Alertmanager receivers configured (Slack/email/PagerDuty)
- [ ] SSL/TLS certificates obtained (Let's Encrypt recommended)
- [ ] Reverse proxy configured (nginx/traefik)
- [ ] Database backups automated
- [ ] Monitoring dashboards verified
- [ ] Secrets stored in env vars or secrets manager

### Docker Deployment

```bash
# Build image
docker build -t ai-ocean:latest .

# Run container
docker run -d \
  --name ocean-backend \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/ocean" \
  -e LOG_LEVEL="info" \
  ai-ocean:latest \
  python3 backend/main.py
```

### Kubernetes Deployment

See `deploy/k8s/` for manifests:

```bash
# Apply Deployment
kubectl apply -f deploy/k8s/deployment.yaml

# Verify
kubectl get pods -l app=ocean-backend
kubectl logs -f deployment/ocean-backend
```

### Environment Variables (Production)

```bash
# Core
DATABASE_URL=postgresql://user:password@prod-db:5432/ocean_db
LOG_LEVEL=info
ENVIRONMENT=production

# Security
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
ALLOWED_HOSTS=api.example.com,dashboard.example.com

# Optional API Keys
NOAA_SST_BASE_URL=...
NOAA_DHW_BASE_URL=...
ALLEN_WFS_URL=...

# Monitoring
PROMETHEUS_RETENTION=30d
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 32)
```

### Backup Strategy

```bash
#!/bin/bash
# Daily backup script

BACKUP_DIR="/backups/ocean"
DATE=$(date +%Y%m%d_%H%M%S)

# Postgres backup
pg_dump -U ocean_user ocean_db | gzip > "$BACKUP_DIR/ocean_db_$DATE.sql.gz"

# Retain 30 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete
```

---

## Troubleshooting

### Backend won't start

```bash
# Check port 8000 available
lsof -i :8000
# Kill process if needed: kill -9 <PID>

# Check database connection
DATABASE_URL=... python3 -c "from backend.database import engine; print(engine.connect())"

# Run with verbose logs
python3 backend/main.py --log-level debug
```

### Pipeline fetches timeout

- **Root cause**: NOAA or Allen APIs slow/unresponsive
- **Immediate fix**: Wait and retry, or use demo data
- **Long-term**: Check upstream API status, consider async fetches

```bash
# Test individual fetches
python3 -c "from pipeline.fetch_noaa import fetch_noaa_crw; print(fetch_noaa_crw())"
```

### Postgres connection refused

```bash
# Check container running
docker ps | grep ocean_db

# Check connection string
psql $DATABASE_URL

# Restart container
docker-compose restart db
```

### Prometheus not scraping metrics

```bash
# Check targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[]'

# Check exporter running
curl http://localhost:8002/metrics

# Verify scrape config
cat AI-DATA-SITE/monitoring/prometheus.yml
```

### Grafana dashboards empty

1. Check data source connection: **Configuration → Data Sources → Prometheus**
2. Test query: `ocean_avg_sst_celsius`
3. Check metrics exporter: `curl http://localhost:8002/metrics | grep ocean_`
4. Re-import dashboard from `monitoring/grafana/dashboards/`

### High disk usage

```bash
# Find large files
du -sh AI-DATA-SITE/* | sort -h

# Clean old NOAA files
rm AI-DATA-SITE/NOAA_*.nc

# Reduce Prometheus retention
# Edit monitoring/prometheus.yml: --storage.tsdb.retention.time=7d
docker-compose restart prometheus
```

---

## Support & Resources

- **Code Issues**: GitHub Issues
- **Monitoring Docs**: Prometheus (https://prometheus.io/docs/), Grafana (https://grafana.com/docs/)
- **Database**: PostGIS (https://postgis.net/), SQLAlchemy (https://sqlalchemy.org/)
- **Deployment**: Docker (https://docs.docker.com/), Kubernetes (https://kubernetes.io/docs/)

---

**Last Updated**: 2026-02-07
**Version**: 1.0.0
