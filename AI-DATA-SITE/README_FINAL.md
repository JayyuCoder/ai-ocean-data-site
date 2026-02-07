# AI Ocean Data Site - Production Ready
**Comprehensive Coral Reef Health Monitoring Platform with Real-time Data Pipeline, Monitoring Stack, and Alerting**

---

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [System Components](#system-components)
- [Deployment](#deployment)
- [Operations & Maintenance](#operations--maintenance)
- [Monitoring & Alerts](#monitoring--alerts)
- [Troubleshooting](#troubleshooting)
- [Project Status](#project-status)

---

## Overview

AI Ocean Data Site is a **production-ready** platform for monitoring coral reef health using real-time ocean data (SST, pH, DHW) from NOAA and Allen Coral Atlas, combined with health scoring algorithms and anomaly detection.

**Key Capabilities:**
- ✅ Real-time NOAA + Allen data ingestion (with exponential backoff retry)
- ✅ Live Streamlit dashboard + FastAPI backend
- ✅ Multi-database support (SQLite + PostgreSQL with PostGIS)
- ✅ Hourly data updates via APScheduler
- ✅ Production-grade monitoring (Prometheus + Grafana)
- ✅ Alerting system (Alertmanager + configurable receivers)
- ✅ UPSERT support to prevent duplicate measurements
- ✅ Data retention/archival policies
- ✅ Kubernetes-ready deployment manifests
- ✅ GitHub Actions CI/CD pipelines

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ DATA SOURCES                                                    │
├─────────────────┬──────────────────────┬────────────────────────┤
│ NOAA CRW API    │ Allen Coral Atlas    │ Local Demo Data        │
│ (SST, DHW, pH)  │ (Reef Geospatial)    │ (Fallback)             │
└────────┬────────┴──────────┬───────────┴────────────┬───────────┘
         │                   │                        │
         └───────────────────┼────────────────────────┘
                             │
              ┌──────────────▼──────────────┐
              │   DATA PIPELINE (Hourly)   │
              │  • Fetch with retries      │
              │  • Transform & merge       │
              │  • Health scoring          │
              │  • Anomaly detection       │
              └──────────────┬──────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────▼─────┐    ┌──────▼──────┐   ┌──────▼──────┐
    │  SQLite   │    │  PostgreSQL │   │  Ocean Metrics
    │(Demo DB)  │    │  + PostGIS  │   │  (Prometheus)
    └───────────┘    └──────┬──────┘   └──────┬───────┘
                            │                  │
          ┌─────────────────┼──────────────────┘
          │                 │
    ┌─────▼──────┐    ┌─────▼──────┐
    │FastAPI     │    │Prometheus  │
    │Backend     │    │+Alertmanager
    │(:8000)     │    │(:9090,:9093)
    └──┬──────┬──┘    └─────┬──────┘
       │      │             │
       │  ┌───▼──────────┐  │
       │  │  Streamlit   │  │
       │  │  Dashboard   │  │
       │  │  (:8501)     │  │
       │  └──────────────┘  │
       │                    │
       └───────────┬────────┘
                   │
              ┌────▼─────────┐
              │  Grafana     │
              │ Dashboards   │
              │  (:3000)     │
              └──────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Data Source** | NOAA CRW, Allen Atlas WFS | Real-time ocean metrics |
| **Storage** | PostgreSQL (+PostGIS) / SQLite | Persistent data + spatial queries |
| **API** | FastAPI + Uvicorn | RESTful backend on :8000 |
| **Frontend** | Streamlit + Plotly + Pydeck | Interactive dashboard on :8501 |
| **Pipeline Orchestration** | APScheduler | Hourly/daily job scheduling |
| **Metrics Export** | prometheus_client | Expose app metrics on :8002 |
| **Monitoring** | Prometheus | Time-series metrics on :9090 |
| **Visualization** | Grafana | Dashboards on :3000 |
| **Alerting** | Alertmanager | Route/group alerts, send notifications on :9093 |
| **Containerization** | Docker + Docker Compose | Local dev + production |
| **CI/CD** | GitHub Actions | Automated tests, builds, deployments |
| **Deployment** | Kubernetes | Production orchestration |

---

## Quick Start

### Minimal Setup (5 minutes)

```bash
# 1. Clone
git clone https://github.com/JayyuCoder/ai-ocean-data-site.git
cd ai-ocean-data-site/AI-DATA-SITE

# 2. Create environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run services (4 terminals)
python3 backend/main.py              # Terminal 1 - Backend API
python3 frontend/app.py              # Terminal 2 - Frontend dashboard
python3 monitoring/metrics_server.py  # Terminal 3 - Metrics exporter
python3 scheduler/scheduler.py       # Terminal 4 - Data pipeline scheduler

# 5. Open dashboard
# http://localhost:8501
```

### Full Stack Setup (with Monitoring)

```bash
# Start Docker services (Postgres, Prometheus, Grafana, Alertmanager)
docker-compose up -d

# Set Postgres URL and run services
export DATABASE_URL=postgresql://ocean_user:ocean_secure_password@localhost:5432/ocean_db
python3 backend/main.py
python3 frontend/app.py
python3 monitoring/metrics_server.py
python3 scheduler/scheduler.py

# Access points:
# - Dashboard: http://localhost:8501
# - Backend API: http://localhost:8000
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)
# - Alertmanager: http://localhost:9093
```

---

## System Components

### 1. Data Pipeline (`pipeline/`)

**Features:**
- Fetches NOAA CRW SST, DHW, pH data
- Fetches Allen Coral Atlas reef polygons
- Spatial merge (point-in-polygon join)
- Health score calculation: `baseline - (SST*1.5 + DHW*5)`
- Anomaly detection (flagged if health < 70)
- **Retry logic**: Exponential backoff (1s→2s→4s) with 3 max attempts
- **UPSERT support**: Prevents duplicate (date, lat, lon) entries on Postgres

**Key Files:**
- `fetch_noaa.py` — NOAA API fetching
- `fetch_allen.py` — Allen Coral Atlas WFS fetching
- `clean_transform.py` — Data processing
- `run_pipeline_light.py` — Main lightweight runner
- `merge_data.py` — Spatial joins

**Usage:**
```bash
# Manual run
python3 pipeline/run_pipeline_light.py

# With Postgres
DATABASE_URL=postgresql://... python3 pipeline/run_pipeline_light.py

# Via scheduler (hourly)
python3 scheduler/scheduler.py
```

### 2. Backend API (`backend/`)

**Endpoints:**
- `GET /health` — Health check
- `GET /data/latest` — Latest measurement
- `GET /data/timeseries?days=7` — Time series (default 7 days)
- `GET /stats` — Aggregate statistics
- `GET /data/anomalies?days=7` — Flagged anomalies

**Database Support:**
- **SQLite** (default, local): `ocean_demo.db`
- **PostgreSQL** (recommended): Set `DATABASE_URL` env var

**Models:** Defined in `models.py` with unique constraint on `(date, latitude, longitude)`

### 3. Frontend (`frontend/`)

**Technologies:** Streamlit, Plotly, Pydeck

**Pages:**
- **Live Map** — Real-time reef locations with SST/pH/health overlays
- **Time Series** — Historical trends (3-day rolling metrics)
- **Anomalies** — Detected anomalies with charts
- **Statistics** — Aggregate metrics and distributions

**Usage:**
```bash
streamlit run frontend/app.py
# Opens on http://localhost:8501
```

### 4. Monitoring Stack

#### Prometheus (`monitoring/prometheus.yml`)
- Scrapes metrics exporter on :8002
- Alert rules defined in `alert_rules.yml`
- Alertmanager configuration in `alertmanager.yml`
- Retention: Configurable (default 30d)

**Key Metrics:**
- `ocean_avg_sst_celsius` — Average SST
- `ocean_avg_ph` — Average pH
- `ocean_avg_health_score` — Reef health
- `ocean_records_total` — Measurement count
- `ocean_sst_last_day_celsius{day="..."}` — Per-day SST
- `ai_pipeline_fetches_total{source="noaa|allen"}` — Fetch attempts
- `ai_pipeline_fetch_retries_total{source="...", reason="timeout|http_429|..."}` — Retry counts
- `ai_pipeline_fetch_failures_total{source="..."}` — Fetch failures

#### Grafana (`monitoring/grafana/dashboards/`)
- **Ocean Overview** — Live SST, pH, health, anomalies
- **Ocean Trends** — 3-day rolling averages
- **Ocean Live** — Real-time per-day metrics

#### Alertmanager (`monitoring/alertmanager.yml`)
- Alert routing by severity (critical/warning)
- **Alert Rules**:
  - `HighSST`: avg_sst > 29°C for 10+ min
  - `ManyAnomalies`: Anomalies rate > 100/hour
- **Receiver Examples** (commented):
  - Slack webhooks
  - Email (SMTP)
  - PagerDuty

### 5. Scheduler (`scheduler/`)

**Modes:**
- **Hourly** (live mode): Fetches and updates data every hour
- **Daily** (default): Scheduled cron job

**Features:**
- Automatic retry on fetch failure
- Logs to `logs/scheduler.log`
- Respects database configuration

```bash
# Test (runs once)
python3 pipeline/run_pipeline_light.py

# Hourly scheduler
python3 scheduler/scheduler.py
```

### 6. Scripts (`scripts/`)

#### `migrate_sqlite_to_postgres.py`
```bash
# Migrate SQLite demo DB → Postgres
DATABASE_URL=postgresql://... python3 scripts/migrate_sqlite_to_postgres.py
```

#### `data_retention.py`
```bash
# Show retention status
python3 scripts/data_retention.py --status

# Delete records older than 90 days
python3 scripts/data_retention.py --delete-days 90

# Archive records older than 90 days (to CSV.gz)
python3 scripts/data_retention.py --archive-days 90 --archive-dir ./archives
```

---

## Deployment

### Local Development

```bash
# SQLite (fastest, no dependencies)
python3 backend/main.py
python3 frontend/app.py

# PostgreSQL (recommended for testing)
docker-compose up -d db
export DATABASE_URL=postgresql://ocean_user:ocean_secure_password@localhost:5432/ocean_db
python3 backend/main.py
python3 frontend/app.py
```

### Docker Deployment

```bash
# Build image
docker build -t ai-ocean:latest .

# Run single container
docker run -d \
  --name ocean-backend \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/ocean" \
  ai-ocean:latest \
  python3 backend/main.py

# Or use docker-compose
docker-compose up -d
```

### Kubernetes Deployment

```bash
# Prerequisites: kubectl, helm (optional)

# Apply manifests
kubectl apply -f deploy/k8s/namespace.yaml
kubectl apply -f deploy/k8s/deployment.yaml
kubectl apply -f deploy/k8s/service.yaml

# Verify
kubectl get pods -n ai-ocean
kubectl logs -f -n ai-ocean deployment/ocean-backend

# Expose via ingress (optional)
kubectl apply -f deploy/k8s/ingress.yaml
```

**Production Environment Variables:**
```bash
DATABASE_URL=postgresql://prod_user:${DB_PASSWORD}@prod-db.internal:5432/ocean_prod
ENVIRONMENT=production
LOG_LEVEL=info
SECRET_KEY=$(openssl rand -base64 32)
ALLOWED_HOSTS=api.example.com,dashboard.example.com
```

---

## Operations & Maintenance

### Backup & Recovery

```bash
# Daily Postgres backup
pg_dump -U ocean_user ocean_db | gzip > backup_$(date +%Y%m%d).sql.gz

# Restore from backup
gunzip < backup_20260207.sql.gz | psql -U ocean_user ocean_db
```

### Data Retention

```bash
# Default policy: Keep last 90 days
python3 scripts/data_retention.py --status

# Archive old data
python3 scripts/data_retention.py --archive-days 90 --archive-dir /backups

# Delete old data (after archive)
python3 scripts/data_retention.py --delete-days 90
```

### Scaling

- **Horizontal**: Add more scheduler instances (DGC/k8s)
- **Vertical**: Increase DB connection pool, RAM for backend
- **Caching**: Consider Redis for metrics caching
- **Batching**: Increase pipeline batch size

### Monitoring Health

```bash
# Backend health
curl http://localhost:8000/health

# Database
DATABASE_URL=... python3 -c "from backend.database import engine; print(engine.connect())"

# Metrics exporter
curl http://localhost:8002/metrics | grep ocean_

# Prometheus targets
curl http://localhost:9090/api/v1/targets
```

---

## Monitoring & Alerts

### Configure Alert Receivers

#### Slack

```yaml
# monitoring/alertmanager.yml
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
3. Create webhook for channel
4. Copy URL into `alertmanager.yml`
5. Restart: `docker-compose restart alertmanager`

#### Email

```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'app-password'

receivers:
  - name: 'warning'
    email_configs:
      - to: 'team@example.com'
        headers:
          Subject: '⚠️ {{ .GroupLabels.alertname }}'
```

### Query Metrics

```promql
# Fetch success rate
rate(ai_pipeline_fetches_total[5m])

# Retry rate by reason
rate(ai_pipeline_fetch_retries_total[5m]) by (reason)

# Fetch failures
ai_pipeline_fetch_failures_total

# Ocean data metrics
ocean_avg_sst_celsius
ocean_avg_health_score
```

---

## Troubleshooting

### Pipeline Timeouts

**Problem**: Fetch operations timeout or hang

**Solution**:
- Check upstream API status (NOAA, Allen)
- Verify network connectivity: `curl https://www.noaa.gov`
- Check timeout settings in `fetch_*.py` (default 60s)
- Review retry logs for specific errors

```bash
# Test individual fetch
DATABASE_URL=... python3 -c "from pipeline.fetch_noaa import fetch_noaa_crw; print(fetch_noaa_crw())"
```

### Database Connection Issues

**Problem**: `psycopg2.OperationalError: Connection refused`

**Solution**:
```bash
# Check Postgres running
docker ps | grep ocean_db

# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Restart container
docker-compose restart db
```

### Prometheus Not Scraping

**Problem**: Prometheus says "up=0" for targets

**Solution**:
```bash
# Check exporter running
curl http://localhost:8002/metrics | head

# Check Prometheus config
cat monitoring/prometheus.yml

# Check firewall/networking
docker network ls  # Ensure containers on same network
```

### High Disk Usage

**Problem**: Disk filling up

**Solution**:
```bash
# Find large files
du -sh /var/lib/postgresql/*  # Check DB size

# Archive old data
python3 scripts/data_retention.py --archive-days 60 --archive-dir /backups

# Delete archived
python3 scripts/data_retention.py --delete-days 60

# Reduce Prometheus retention (optional)
# Edit docker-compose.yml: --storage.tsdb.retention.time=7d
docker-compose restart prometheus
```

### Alertmanager Not Sending Notifications

**Problem**: Alerts fire but no notifications received

**Solution**:
1. Check Alertmanager is running: `curl http://localhost:9093/`
2. Verify receiver config: `cat monitoring/alertmanager.yml`
3. Test webhook endpoint: Alertmanager logs should show retry attempts
4. Check credentials (Slack token, email password)

---

## Project Status

### ✅ Implemented (Production Ready)

- Core API endpoints
- Streamlit dashboard
- Data pipeline with retry logic
- SQLite + Postgres support
- UPSERT to prevent duplicates
- APScheduler for hourly updates
- Prometheus metrics + Grafana dashboards
- Alertmanager configuration
- Docker Compose for local dev
- Kubernetes manifests + GitHub Actions CI/CD
- Data migration utilities
- Data retention/archival policies
- Comprehensive documentation

### 🚀 Optional Enhancements (Future)

- Async/concurrent fetching (reduce latency)
- WebSocket live updates (replace polling)
- Time-series forecasting (LSTM models)
- Advanced anomaly detection (Isolation Forest)
- Multi-region deployment
- API rate limiting & caching
- Admin dashboard for operations
- Machine learning model serving (FastAPI + TensorFlow)

---

## Quick Reference

| Task | Command |
|------|---------|
| **Start development** | `docker-compose up -d && python3 backend/main.py` |
| **Run pipeline** | `DATABASE_URL=... python3 pipeline/run_pipeline_light.py` |
| **Test health** | `curl http://localhost:8000/health` |
| **View logs** | `tail -f logs/scheduler.log` |
| **Migrate DB** | `DATABASE_URL=... python3 scripts/migrate_sqlite_to_postgres.py` |
| **Retention policy** | `python3 scripts/data_retention.py --status` |
| **Deploy to K8s** | `kubectl apply -f deploy/k8s/` |
| **Build Docker image** | `docker build -t ai-ocean:latest .` |

---

## Support & Resources

- **GitHub**: https://github.com/JayyuCoder/ai-ocean-data-site
- **Deployment Guide**: [DEPLOYMENT_OPS_GUIDE.md](DEPLOYMENT_OPS_GUIDE.md)
- **System Status**: [COMPLETE_CHECK.md](../COMPLETE_CHECK.md)
- **Monitoring**: Prometheus (https://prometheus.io/docs/), Grafana (https://grafana.com/docs/)
- **Data Sources**: NOAA CRW (https://www.star.nesdis.noaa.gov/), Allen Institute (https://allencoralatlas.org/)

---

**Version**: 1.0.0  
**Status**: 🟢 Production Ready  
**Last Updated**: 2026-02-07
